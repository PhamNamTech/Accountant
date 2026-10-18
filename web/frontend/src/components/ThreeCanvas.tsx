import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

export const ThreeCanvas: React.FC = () => {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const currentMount = mountRef.current;
    if (!currentMount) return;

    // Scene, Camera, Renderer
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      45,
      currentMount.clientWidth / currentMount.clientHeight,
      0.1,
      1000
    );
    camera.position.z = 18;

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(currentMount.clientWidth, currentMount.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    currentMount.appendChild(renderer.domElement);

    // Group for objects
    const mainGroup = new THREE.Group();
    scene.add(mainGroup);

    // 1. Central Icosahedron (Financial Core)
    const coreGeo = new THREE.IcosahedronGeometry(2.4, 1);
    const coreMat = new THREE.MeshStandardMaterial({
      color: 0x10b981, // Emerald
      wireframe: true,
      transparent: true,
      opacity: 0.65,
      roughness: 0.2,
      metalness: 0.8,
    });
    const coreMesh = new THREE.Mesh(coreGeo, coreMat);
    mainGroup.add(coreMesh);

    // Inner Glowing Core
    const innerGeo = new THREE.OctahedronGeometry(1.2, 0);
    const innerMat = new THREE.MeshBasicMaterial({
      color: 0x06b6d4, // Cyan
      wireframe: false,
      transparent: true,
      opacity: 0.75,
    });
    const innerMesh = new THREE.Mesh(innerGeo, innerMat);
    mainGroup.add(innerMesh);

    // 2. Floating Satellite Nodes (Representing Accounts 112, 155, 621, 622, 627, 154)
    const satellites: Array<{ mesh: THREE.Mesh; orbitRadius: number; speed: number; angle: number; yOffset: number }> = [];
    const nodeColors = [0x10b981, 0x06b6d4, 0x6366f1, 0x3b82f6, 0x14b8a6, 0x8b5cf6];

    for (let i = 0; i < 6; i++) {
      const satGeo = new THREE.BoxGeometry(0.55, 0.55, 0.55);
      const satMat = new THREE.MeshStandardMaterial({
        color: nodeColors[i % nodeColors.length],
        roughness: 0.3,
        metalness: 0.7,
        transparent: true,
        opacity: 0.85,
      });
      const satMesh = new THREE.Mesh(satGeo, satMat);
      mainGroup.add(satMesh);

      satellites.push({
        mesh: satMesh,
        orbitRadius: 4.5 + (i % 3) * 0.8,
        speed: 0.008 + i * 0.003,
        angle: (i * Math.PI) / 3,
        yOffset: ((i - 2.5) * 0.8),
      });
    }

    // 3. Floating Antigravity Particles Constellation
    const particleCount = 220;
    const posArray = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount * 3; i += 3) {
      posArray[i] = (Math.random() - 0.5) * 22;
      posArray[i + 1] = (Math.random() - 0.5) * 16;
      posArray[i + 2] = (Math.random() - 0.5) * 16;
    }

    const particleGeo = new THREE.BufferGeometry();
    particleGeo.setAttribute('position', new THREE.BufferAttribute(posArray, 3));

    const particleMat = new THREE.PointsMaterial({
      size: 0.06,
      color: 0x38bdf8,
      transparent: true,
      opacity: 0.45,
    });
    const particleSystem = new THREE.Points(particleGeo, particleMat);
    mainGroup.add(particleSystem);

    // 4. Subtle Ambient & Point Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);

    const pointLightEmerald = new THREE.PointLight(0x10b981, 3, 30);
    pointLightEmerald.position.set(5, 5, 5);
    scene.add(pointLightEmerald);

    const pointLightCyan = new THREE.PointLight(0x06b6d4, 2.5, 30);
    pointLightCyan.position.set(-5, -5, 5);
    scene.add(pointLightCyan);

    // Mouse Tracking with Inertial Damping (Antigravity physics)
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;

    const handleMouseMove = (event: MouseEvent) => {
      const rect = currentMount.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width - 0.5;
      const y = (event.clientY - rect.top) / rect.height - 0.5;
      mouseX = x * 2;
      mouseY = y * 2;
    };

    window.addEventListener('mousemove', handleMouseMove);

    // Resize Handler
    const handleResize = () => {
      if (!currentMount) return;
      camera.aspect = currentMount.clientWidth / currentMount.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(currentMount.clientWidth, currentMount.clientHeight);
    };

    window.addEventListener('resize', handleResize);

    // Animation Loop
    let animationFrameId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const elapsedTime = clock.getElapsedTime();

      // Smooth mouse follow (spring inertia)
      targetX += (mouseX - targetX) * 0.04;
      targetY += (mouseY - targetY) * 0.04;

      mainGroup.rotation.y = elapsedTime * 0.12 + targetX * 0.8;
      mainGroup.rotation.x = targetY * 0.5;

      // Antigravity buoyant levitation for core
      coreMesh.position.y = Math.sin(elapsedTime * 1.5) * 0.25;
      coreMesh.rotation.y += 0.005;
      coreMesh.rotation.x += 0.003;

      innerMesh.rotation.y -= 0.01;
      innerMesh.rotation.z += 0.008;

      // Rotate and float satellites
      satellites.forEach((sat, idx) => {
        sat.angle += sat.speed;
        sat.mesh.position.x = Math.cos(sat.angle) * sat.orbitRadius;
        sat.mesh.position.z = Math.sin(sat.angle) * sat.orbitRadius;
        sat.mesh.position.y = sat.yOffset + Math.sin(elapsedTime * 2 + idx) * 0.35;

        sat.mesh.rotation.x += 0.02;
        sat.mesh.rotation.y += 0.015;
      });

      // Gently drift particles
      particleSystem.rotation.y = elapsedTime * 0.03;

      renderer.render(scene, camera);
    };

    animate();

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
      if (currentMount && renderer.domElement) {
        currentMount.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, []);

  return (
    <div
      ref={mountRef}
      className="w-full h-full min-h-[340px] relative pointer-events-auto cursor-grab active:cursor-grabbing"
      title="Khối tương tác 3D ThreeUI - Di chuột để điều hướng trọng lực"
    />
  );
};
