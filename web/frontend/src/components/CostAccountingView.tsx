import React, { useState } from 'react';
import {
  Calculator,
  Download,
  AlertTriangle,
  CheckCircle2,
  PieChart,
  ArrowRight,
  Sparkles,
  Sliders,
  Layers,
  FileSpreadsheet,
  Gauge,
  Info,
} from 'lucide-react';

export const CostAccountingView: React.FC = () => {
  const [productName, setProductName] = useState('Bàn gỗ sồi');
  const [slHoanThanh, setSlHoanThanh] = useState<number>(1000);
  const [dDauKy, setDDauKy] = useState<number>(10000000);
  const [cpNvl, setCpNvl] = useState<number>(50000000);
  const [cpNc, setCpNc] = useState<number>(20000000);
  const [cpSxc, setCpSxc] = useState<number>(12000000);
  const [dCuoiKy, setDCuoiKy] = useState<number>(11000000);
  const [pheLieu, setPheLieu] = useState<number>(1000000);
  const [regime, setRegime] = useState<'TT99' | 'TT200' | 'TT133'>('TT99');

  // VAS 02 Normal Capacity Mode
  const [vas02Enabled, setVas02Enabled] = useState(false);
  const [congSuatThucTe, setCongSuatThucTe] = useState<number>(800);
  const [congSuatDinhMuc, setCongSuatDinhMuc] = useState<number>(1000);
  const [tyLeSxcCoDinh, setTyLeSxcCoDinh] = useState<number>(50);

  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);

  // Tab switch for Direct Cost vs Overhead Multi-product Allocation
  const [mode, setMode] = useState<'direct' | 'allocate'>('direct');

  // Allocation State
  const [totalOverhead, setTotalOverhead] = useState<number>(30000000);
  const [criteria, setCriteria] = useState<'nvl' | 'nhan_cong' | 'so_luong'>('nvl');
  const [allocProducts] = useState([
    { name: 'Sản phẩm A', base_value: 60000000 },
    { name: 'Sản phẩm B', base_value: 40000000 },
  ]);
  const [allocResult, setAllocResult] = useState<any>(null);

  const handleCalculate = async () => {
    setLoading(true);
    try {
      const payload: any = {
        product_name: productName,
        d_dau_ky: dDauKy,
        cp_nvl_truc_tiep: cpNvl,
        cp_nhan_cong_truc_tiep: cpNc,
        cp_san_xuat_chung: cpSxc,
        d_cuoi_ky: dCuoiKy,
        sl_hoan_thanh: slHoanThanh,
        phe_lieu_thu_hoi: pheLieu,
        regime,
      };

      if (vas02Enabled) {
        payload.cong_suat_thuc_te = congSuatThucTe;
        payload.cong_suat_dinh_muc = congSuatDinhMuc;
        payload.ty_le_sxc_co_dinh = tyLeSxcCoDinh;
      }

      const res = await fetch('/api/cost/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleExportExcel = async () => {
    setDownloading(true);
    try {
      const payload = {
        product_name: productName,
        ky_tinh_gia_thanh: 'Tháng 10/2026',
        sl_hoan_thanh: slHoanThanh,
        d_dau_ky_dict: { nvl: dDauKy * 0.6, nc: dDauKy * 0.25, sxc: dDauKy * 0.15 },
        phat_sinh_dict: { nvl: cpNvl, nc: cpNc, sxc: cpSxc },
        d_cuoi_ky_dict: { nvl: dCuoiKy * 0.6, nc: dCuoiKy * 0.25, sxc: dCuoiKy * 0.15 },
      };

      const res = await fetch('/api/cost/export-excel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `The_Tinh_Gia_Thanh_${productName}.xlsx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err) {
      console.error(err);
    } finally {
      setDownloading(false);
    }
  };

  const handleAllocate = async () => {
    try {
      const res = await fetch('/api/cost/allocate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          total_overhead: totalOverhead,
          criteria,
          products: allocProducts,
        }),
      });
      const data = await res.json();
      setAllocResult(data);
    } catch (err) {
      console.error(err);
    }
  };

  const setPreset1 = () => {
    setProductName('Bàn gỗ sồi');
    setSlHoanThanh(1000);
    setDDauKy(10000000);
    setCpNvl(50000000);
    setCpNc(20000000);
    setCpSxc(12000000);
    setDCuoiKy(11000000);
    setPheLieu(1000000);
    setVas02Enabled(false);
  };

  const setPreset2 = () => {
    setProductName('Tủ tài liệu');
    setSlHoanThanh(500);
    setDDauKy(5000000);
    setCpNvl(30000000);
    setCpNc(10000000);
    setCpSxc(8000000);
    setDCuoiKy(3000000);
    setPheLieu(0);
    setVas02Enabled(false);
  };

  const formatVND = (num: number) => {
    return new Intl.NumberFormat('vi-VN').format(Math.round(num || 0)) + ' ₫';
  };

  const capacityRatio = congSuatDinhMuc > 0 ? (congSuatThucTe / congSuatDinhMuc) * 100 : 100;

  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* Top Banner */}
      <div className="double-bezel">
        <div className="double-bezel-inner p-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-kinpaku/10 border border-kinpaku/30 text-kinpaku text-xs font-mono">
                <Calculator className="w-3.5 h-3.5" />
                <span>Kế Toán Giá Thành & Chuẩn Mực VAS 02</span>
              </div>
              <h2 className="text-2xl font-bold text-champagne mt-2">Tính Giá Thành & Phân Bổ Chi Phí</h2>
              <p className="text-xs text-muted mt-1 max-w-2xl">
                Tập hợp chi phí NVL, Nhân công, Sản xuất chung; phân bổ theo công suất bình thường VAS 02 và tự động định khoản theo TT 99/2025 (TK 155), TT 200/2014 (TK 1551) hoặc TT 133/2016.
              </p>
            </div>

            {/* Mode Switcher */}
            <div className="flex items-center gap-1.5 p-1 rounded-2xl bg-graphite border border-white/[0.08] w-fit">
              <button
                onClick={() => setMode('direct')}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all cursor-pointer ${
                  mode === 'direct'
                    ? 'bg-kinpaku text-on-gold font-bold shadow-[0_0_12px_-2px_rgba(245,196,81,0.4)]'
                    : 'text-muted hover:text-champagne'
                }`}
              >
                Tính Giá Thành (Z, z)
              </button>
              <button
                onClick={() => setMode('allocate')}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all cursor-pointer ${
                  mode === 'allocate'
                    ? 'bg-patina text-on-gold font-bold shadow-[0_0_12px_-2px_rgba(112,192,208,0.4)]'
                    : 'text-muted hover:text-champagne'
                }`}
              >
                Phân Bổ SXC Đa Sản Phẩm
              </button>
            </div>
          </div>

          {/* Formula Callout Banner */}
          <div className="mt-5 p-3 rounded-xl bg-lacquer-deep border border-white/[0.08] flex items-center justify-between flex-wrap gap-2 text-[11px] font-mono text-warm">
            <div className="flex items-center gap-2">
              <span className="text-kinpaku font-bold">CÔNG THỨC VAS 02:</span>
              <span>Z = D_đầu + (C_NVL + C_NC + C_SXC hợp lý) - D_cuối - Phế liệu</span>
            </div>
            <div className="text-patina font-bold">
              z = Z / Q_hoàn_thành
            </div>
          </div>
        </div>
      </div>

      {mode === 'direct' ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Left Form: Inputs */}
          <div className="lg:col-span-6 space-y-5">
            <div className="double-bezel">
              <div className="double-bezel-inner p-5 space-y-4">
                
                {/* Presets and Regime Header */}
                <div className="flex items-center justify-between pb-3 border-b border-white/[0.08] flex-wrap gap-2">
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs text-muted">Nạp mẫu test:</span>
                    <button
                      onClick={setPreset1}
                      className="px-2.5 py-1 rounded bg-graphite hover:bg-graphite-2 text-kinpaku text-[11px] font-mono border border-white/[0.06] cursor-pointer active:scale-95 font-medium"
                    >
                      Bàn gỗ sồi
                    </button>
                    <button
                      onClick={setPreset2}
                      className="px-2.5 py-1 rounded bg-graphite hover:bg-graphite-2 text-patina text-[11px] font-mono border border-white/[0.06] cursor-pointer active:scale-95 font-medium"
                    >
                      Tủ tài liệu
                    </button>
                  </div>

                  {/* Regime select */}
                  <div className="flex items-center gap-1 text-[11px]">
                    <span className="text-muted">Chế độ:</span>
                    <select
                      value={regime}
                      onChange={(e: any) => setRegime(e.target.value)}
                      className="bg-graphite border border-white/10 text-kinpaku px-2 py-1 rounded font-mono text-xs focus:outline-none"
                    >
                      <option value="TT99">TT 99/2025 (TK 155 Sản phẩm)</option>
                      <option value="TT200">TT 200/2014 (TK 1551 Thành phẩm)</option>
                      <option value="TT133">TT 133/2016 (TK 154 chi tiết)</option>
                    </select>
                  </div>
                </div>

                {/* Form Fields */}
                {/* Form Fields */}
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="col-span-2 sm:col-span-1">
                    <label className="block text-muted mb-1">Tên sản phẩm</label>
                    <input
                      type="text"
                      value={productName}
                      onChange={(e) => setProductName(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl bg-graphite border border-white/10 text-champagne font-medium focus:outline-none focus:border-kinpaku/50"
                    />
                  </div>

                  <div className="col-span-2 sm:col-span-1">
                    <label className="block text-muted mb-1">Sản lượng hoàn thành (Q)</label>
                    <input
                      type="number"
                      value={slHoanThanh}
                      onChange={(e) => setSlHoanThanh(Number(e.target.value))}
                      className="w-full px-3 py-2 rounded-xl bg-graphite border border-white/10 text-champagne font-mono focus:outline-none focus:border-kinpaku/50"
                    />
                  </div>

                  <div>
                    <label className="block text-muted mb-1">Dở dang đầu kỳ (D_đk)</label>
                    <input
                      type="number"
                      value={dDauKy}
                      onChange={(e) => setDDauKy(Number(e.target.value))}
                      className="w-full px-3 py-2 rounded-xl bg-graphite border border-white/10 text-champagne font-mono focus:outline-none focus:border-kinpaku/50"
                    />
                  </div>

                  <div>
                    <label className="block text-muted mb-1">Dở dang cuối kỳ (D_ck)</label>
                    <input
                      type="number"
                      value={dCuoiKy}
                      onChange={(e) => setDCuoiKy(Number(e.target.value))}
                      className="w-full px-3 py-2 rounded-xl bg-graphite border border-white/10 text-champagne font-mono focus:outline-none focus:border-kinpaku/50"
                    />
                  </div>

                  <div className="col-span-2">
                    <div className="p-3 rounded-xl bg-lacquer-deep border border-hairline space-y-2.5">
                      <p className="text-[11px] font-semibold text-champagne">Chi Phí Phát Sinh Trong Kỳ (C)</p>
                      
                      <div className="grid grid-cols-3 gap-2">
                        <div>
                          <span className="text-[10px] text-muted">NVL Trực Tiếp (621)</span>
                          <input
                            type="number"
                            value={cpNvl}
                            onChange={(e) => setCpNvl(Number(e.target.value))}
                            className="w-full mt-1 px-2.5 py-1.5 rounded-lg bg-graphite border border-white/10 text-champagne font-mono text-xs focus:outline-none focus:border-kinpaku/50"
                          />
                        </div>
                        <div>
                          <span className="text-[10px] text-muted">Nhân Công TT (622)</span>
                          <input
                            type="number"
                            value={cpNc}
                            onChange={(e) => setCpNc(Number(e.target.value))}
                            className="w-full mt-1 px-2.5 py-1.5 rounded-lg bg-graphite border border-white/10 text-champagne font-mono text-xs focus:outline-none focus:border-kinpaku/50"
                          />
                        </div>
                        <div>
                          <span className="text-[10px] text-muted">SX Chung (627)</span>
                          <input
                            type="number"
                            value={cpSxc}
                            onChange={(e) => setCpSxc(Number(e.target.value))}
                            className="w-full mt-1 px-2.5 py-1.5 rounded-lg bg-graphite border border-white/10 text-champagne font-mono text-xs focus:outline-none focus:border-kinpaku/50"
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="col-span-2">
                    <label className="block text-muted mb-1">Phế liệu thu hồi (nếu có)</label>
                    <input
                      type="number"
                      value={pheLieu}
                      onChange={(e) => setPheLieu(Number(e.target.value))}
                      className="w-full px-3 py-2 rounded-xl bg-graphite border border-white/10 text-champagne font-mono focus:outline-none focus:border-kinpaku/50"
                    />
                  </div>
                </div>

                {/* VAS 02 Capacity Control Toggle */}
                <div className="p-3.5 rounded-xl bg-patina/5 border border-patina/25 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Sliders className="w-4 h-4 text-patina" />
                      <div>
                        <span className="text-xs font-semibold text-champagne block">Kiểm Soát Công Suất Bình Thường (VAS 02)</span>
                        <span className="text-[10px] text-muted">Loại trừ SXC cố định dưới công suất vào TK 632</span>
                      </div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={vas02Enabled}
                        onChange={(e) => setVas02Enabled(e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-9 h-5 bg-graphite peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-patina"></div>
                    </label>
                  </div>

                  {vas02Enabled && (
                    <div className="pt-2 border-t border-patina/20 space-y-3 text-xs">
                      <div className="grid grid-cols-3 gap-2">
                        <div>
                          <span className="text-[10px] text-muted">Công suất thực tế</span>
                          <input
                            type="number"
                            value={congSuatThucTe}
                            onChange={(e) => setCongSuatThucTe(Number(e.target.value))}
                            className="w-full mt-1 px-2.5 py-1.5 rounded-lg bg-graphite border border-patina/30 text-champagne font-mono text-xs focus:outline-none"
                          />
                        </div>
                        <div>
                          <span className="text-[10px] text-muted">Công suất định mức</span>
                          <input
                            type="number"
                            value={congSuatDinhMuc}
                            onChange={(e) => setCongSuatDinhMuc(Number(e.target.value))}
                            className="w-full mt-1 px-2.5 py-1.5 rounded-lg bg-graphite border border-patina/30 text-champagne font-mono text-xs focus:outline-none"
                          />
                        </div>
                        <div>
                          <span className="text-[10px] text-muted">Tỷ lệ SXC cố định (%)</span>
                          <input
                            type="number"
                            value={tyLeSxcCoDinh}
                            onChange={(e) => setTyLeSxcCoDinh(Number(e.target.value))}
                            className="w-full mt-1 px-2.5 py-1.5 rounded-lg bg-graphite border border-patina/30 text-champagne font-mono text-xs focus:outline-none"
                          />
                        </div>
                      </div>

                      {/* Bullet Capacity Utilization Indicator */}
                      <div className="p-2.5 rounded-lg bg-lacquer-deep border border-hairline space-y-1">
                        <div className="flex justify-between text-[11px] font-mono">
                          <span className="text-muted">Hiệu suất công suất:</span>
                          <span className={capacityRatio < 100 ? 'text-vermilion font-bold' : 'text-patina font-bold'}>
                            {capacityRatio.toFixed(1)}% {capacityRatio < 100 ? '(Dưới định mức)' : '(Đạt chuẩn)'}
                          </span>
                        </div>
                        <div className="h-1.5 w-full bg-graphite rounded-full overflow-hidden">
                          <div
                            style={{ width: `${Math.min(capacityRatio, 100)}%` }}
                            className={`h-full ${capacityRatio < 100 ? 'bg-vermilion' : 'bg-patina'}`}
                          />
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Calculate CTA */}
                <button
                  onClick={handleCalculate}
                  disabled={loading}
                  className="w-full py-3 rounded-xl bg-kinpaku hover:bg-kinpaku-vivid text-on-gold font-bold text-xs uppercase tracking-wider transition-all duration-300 shadow-[0_0_20px_-3px_rgba(245,196,81,0.4)] active:scale-98 cursor-pointer flex items-center justify-center gap-2"
                >
                  <Calculator className="w-4 h-4" />
                  <span>{loading ? 'Đang Tính Toán...' : 'Thực Hiện Tính Giá Thành (Z, z)'}</span>
                </button>

              </div>
            </div>
          </div>

          {/* Right Display: Results */}
          <div className="lg:col-span-6 space-y-5">
            {result ? (
              <div className="double-bezel">
                <div className="double-bezel-inner p-6 space-y-6">
                  
                  {/* Result Header */}
                  <div className="flex items-center justify-between pb-4 border-b border-white/[0.08] flex-wrap gap-2">
                    <div>
                      <span className="text-[11px] font-mono text-kinpaku">KẾT QUẢ TÍNH TOÁN GIÁ THÀNH</span>
                      <h3 className="text-xl font-bold text-champagne mt-0.5">{result.san_pham}</h3>
                    </div>
                    <span className="text-xs font-mono px-2.5 py-1 rounded bg-kinpaku/15 text-kinpaku border border-kinpaku/30 font-bold">
                      {result.che_do_ke_toan}
                    </span>
                  </div>

                  {/* Main Metric Cards: Z and z */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 rounded-xl bg-kinpaku/10 border border-kinpaku/30">
                      <p className="text-[11px] text-muted uppercase tracking-wider">Tổng Giá Thành (Z)</p>
                      <p className="text-2xl font-extrabold text-kinpaku font-mono mt-1 tabular-nums">
                        {formatVND(result.tong_gia_thanh_Z)}
                      </p>
                      <p className="text-[10px] text-faint mt-1 font-mono">Q = {result.so_luong_hoan_thanh} SP</p>
                    </div>

                    <div className="p-4 rounded-xl bg-patina/10 border border-patina/30">
                      <p className="text-[11px] text-muted uppercase tracking-wider">Giá Thành Đơn Vị (z)</p>
                      <p className="text-2xl font-extrabold text-patina font-mono mt-1 tabular-nums">
                        {formatVND(result.gia_thanh_don_vi_z)}
                      </p>
                      <p className="text-[10px] text-faint mt-1 font-mono">/ đơn vị hoàn thành</p>
                    </div>
                  </div>

                  {/* VAS 02 Notice if applied */}
                  {result.vas02_info?.applied && (
                    <div className="p-3.5 rounded-xl bg-vermilion/15 border border-vermilion/30 text-xs text-champagne space-y-1">
                      <div className="flex items-center gap-1.5 font-semibold text-vermilion">
                        <AlertTriangle className="w-4 h-4 text-vermilion shrink-0" />
                        <span>Áp Dụng VAS 02: Sản Xuất Dưới Công Suất Bình Thường</span>
                      </div>
                      <p className="text-[11px] leading-relaxed text-warm">
                        Chi phí SXC cố định lãng phí <strong className="font-mono text-champagne">{formatVND(result.vas02_info.sxc_duoi_cong_suat_tinh_vao_632)}</strong> được chuyển thẳng vào <strong className="text-vermilion">Giá vốn hàng bán (TK 632)</strong>, tuyệt đối không tính vào giá thành sản phẩm (TK 154/TK 155).
                      </p>
                    </div>
                  )}

                  {/* Cost Structure Breakdown Progress Bar */}
                  {result.co_cau_chi_phi_phan_tram && (
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-muted font-medium">Cơ cấu chi phí phát sinh</span>
                        <span className="font-mono text-faint text-[11px]">Tổng 100%</span>
                      </div>

                      <div className="h-2.5 w-full rounded-full bg-graphite overflow-hidden flex">
                        <div
                          style={{ width: `${result.co_cau_chi_phi_phan_tram.ty_trong_nvl}%` }}
                          className="bg-kinpaku h-full"
                          title={`NVL: ${result.co_cau_chi_phi_phan_tram.ty_trong_nvl}%`}
                        />
                        <div
                          style={{ width: `${result.co_cau_chi_phi_phan_tram.ty_trong_nhan_cong}%` }}
                          className="bg-patina h-full"
                          title={`Nhân công: ${result.co_cau_chi_phi_phan_tram.ty_trong_nhan_cong}%`}
                        />
                        <div
                          style={{ width: `${result.co_cau_chi_phi_phan_tram.ty_trong_sx_chung}%` }}
                          className="bg-graphite-2 h-full"
                          title={`SXC: ${result.co_cau_chi_phi_phan_tram.ty_trong_sx_chung}%`}
                        />
                      </div>

                      <div className="flex items-center justify-between text-[11px] text-muted pt-1 font-mono">
                        <span className="text-kinpaku font-medium">● NVL: {result.co_cau_chi_phi_phan_tram.ty_trong_nvl}%</span>
                        <span className="text-patina font-medium">● Nhân công: {result.co_cau_chi_phi_phan_tram.ty_trong_nhan_cong}%</span>
                        <span className="text-warm font-medium">● SXC: {result.co_cau_chi_phi_phan_tram.ty_trong_sx_chung}%</span>
                      </div>
                    </div>
                  )}

                  {/* Accounting Journal Entries */}
                  <div className="space-y-2 pt-2 border-t border-white/[0.08]">
                    <p className="text-xs font-semibold text-champagne">Bút Toán Định Khoản Tự Động:</p>
                    
                    <div className="space-y-1.5 text-xs font-mono">
                      {/* Entry 1: Finished Goods Warehouse Receipt */}
                      <div className="p-3 rounded-lg bg-lacquer-deep border border-white/[0.08] flex items-center justify-between">
                        <div>
                          <span className="text-kinpaku font-bold">
                            Nợ TK {result.but_toan_dinh_khoan?.nhap_kho?.no}
                          </span>
                          {' / '}
                          <span className="text-patina font-bold">
                            Có TK {result.but_toan_dinh_khoan?.nhap_kho?.co}
                          </span>
                          <p className="text-[10px] text-muted mt-0.5">
                            {result.but_toan_dinh_khoan?.nhap_kho?.dien_giai}
                          </p>
                        </div>
                        <span className="text-champagne font-bold tabular-nums">
                          {formatVND(result.but_toan_dinh_khoan?.nhap_kho?.so_tien)}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Export Excel Action */}
                  <button
                    onClick={handleExportExcel}
                    disabled={downloading}
                    className="w-full py-2.5 rounded-xl bg-graphite hover:bg-graphite-2 text-champagne border border-white/10 text-xs font-medium transition-colors flex items-center justify-center gap-2 cursor-pointer active:scale-98"
                  >
                    <FileSpreadsheet className="w-4 h-4 text-kinpaku" />
                    <span>{downloading ? 'Đang tạo Excel...' : 'Tải Thẻ Tính Giá Thành Excel (.xlsx)'}</span>
                  </button>

                </div>
              </div>
            ) : (
              <div className="double-bezel h-full min-h-[380px]">
                <div className="double-bezel-inner p-8 h-full flex flex-col items-center justify-center text-center text-muted text-xs space-y-3">
                  <Calculator className="w-10 h-10 text-faint" />
                  <p>Nhập số liệu hoặc chọn mẫu test và nhấn "Thực Hiện Tính Giá Thành" để xem kết quả Z, z và bút toán định khoản.</p>
                </div>
              </div>
            )}
          </div>

        </div>
      ) : (
        /* Overhead Multi-Product Allocation Mode */
        <div className="double-bezel">
          <div className="double-bezel-inner p-6 space-y-5">
            <h3 className="text-base font-bold text-champagne">Phân Bổ Chi Phí Sản Xuất Chung (TK 627) Cho Nhiều Sản Phẩm</h3>
            <p className="text-xs text-muted">
              Phân bổ tổng chi phí sản xuất chung theo tiêu thức: Chi phí NVL trực tiếp (621), Chi phí nhân công (622), hoặc Số lượng sản phẩm sản xuất.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div>
                <label className="block text-muted mb-1">Tổng chi phí SXC cần phân bổ</label>
                <input
                  type="number"
                  value={totalOverhead}
                  onChange={(e) => setTotalOverhead(Number(e.target.value))}
                  className="w-full px-3 py-2 rounded-xl bg-graphite border border-white/10 text-champagne font-mono focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-muted mb-1">Tiêu thức phân bổ</label>
                <select
                  value={criteria}
                  onChange={(e: any) => setCriteria(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-graphite border border-white/10 text-champagne focus:outline-none"
                >
                  <option value="nvl">Theo Chi Phí NVL Trực Tiếp (TK 621)</option>
                  <option value="nhan_cong">Theo Chi Phí Nhân Công TT (TK 622)</option>
                  <option value="so_luong">Theo Số Lượng Sản Xuất (Q)</option>
                </select>
              </div>

              <div className="flex items-end">
                <button
                  onClick={handleAllocate}
                  className="w-full py-2.5 rounded-xl bg-patina hover:bg-patina-pale text-on-gold font-bold text-xs uppercase tracking-wider transition-colors cursor-pointer active:scale-98 shadow-[0_0_15px_-3px_rgba(112,192,208,0.4)]"
                >
                  Phân Bổ Chi Phí
                </button>
              </div>
            </div>

            {/* Products Base Table */}
            <div className="overflow-x-auto pt-3">
              <table className="w-full text-xs text-left">
                <thead className="bg-lacquer-deep text-[11px] text-faint uppercase border-b border-white/[0.08]">
                  <tr>
                    <th className="py-2.5 px-4">Tên Sản Phẩm</th>
                    <th className="py-2.5 px-4 text-right">Giá Trị Tiêu Thức</th>
                    <th className="py-2.5 px-4 text-right">Tỷ Lệ (%)</th>
                    <th className="py-2.5 px-4 text-right">Chi Phí SXC Được Phân Bổ</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/[0.06]">
                  {allocResult ? (
                    allocResult.ket_qua_phan_bo.map((item: any, idx: number) => (
                      <tr key={idx} className="hover:bg-white/[0.02]">
                        <td className="py-2.5 px-4 font-semibold text-champagne">{item.san_pham}</td>
                        <td className="py-2.5 px-4 text-right font-mono text-warm tabular-nums">
                          {formatVND(item.gia_tri_tieu_thuc)}
                        </td>
                        <td className="py-2.5 px-4 text-right font-mono text-patina font-bold">
                          {item.he_so_phan_bo}%
                        </td>
                        <td className="py-2.5 px-4 text-right font-mono font-bold text-kinpaku tabular-nums">
                          {formatVND(item.chi_phi_sxc_phan_bo)}
                        </td>
                      </tr>
                    ))
                  ) : (
                    allocProducts.map((p, idx) => (
                      <tr key={idx}>
                        <td className="py-2.5 px-4 text-champagne">{p.name}</td>
                        <td className="py-2.5 px-4 text-right font-mono text-muted tabular-nums">
                          {formatVND(p.base_value)}
                        </td>
                        <td className="py-2.5 px-4 text-right text-faint">-</td>
                        <td className="py-2.5 px-4 text-right text-faint">-</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
