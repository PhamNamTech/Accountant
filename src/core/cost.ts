export interface ProductCostInput {
  productName: string;
  dDauKy: number;
  cpNvlTrucTiep: number;
  cpNhanCongTrucTiep: number;
  cpSanXuatChung: number;
  dCuoiKy: number;
  slHoanThanh: number;
  pheLieuThuHoi?: number;
  regime?: string;
  congSuatThucTe?: number | null;
  congSuatDinhMuc?: number | null;
  tyLeSxcCoDinh?: number;
}

export function calculateProductCost(input: ProductCostInput) {
  const {
    productName,
    dDauKy,
    cpNvlTrucTiep,
    cpNhanCongTrucTiep,
    cpSanXuatChung,
    dCuoiKy,
    slHoanThanh,
    pheLieuThuHoi = 0,
    regime = "TT99",
    congSuatThucTe,
    congSuatDinhMuc,
    tyLeSxcCoDinh = 50.0,
  } = input;

  if (slHoanThanh <= 0) {
    throw new Error("Số lượng thành phẩm hoàn thành phải lớn hơn 0");
  }

  // VAS 02 normal capacity logic
  let cpSxcHopLy = cpSanXuatChung;
  let sxcDuoiCongSuat = 0.0;
  let vas02Applied = false;

  if (congSuatThucTe && congSuatDinhMuc && congSuatDinhMuc > 0) {
    if (congSuatThucTe < congSuatDinhMuc) {
      vas02Applied = true;
      const tyLeCoDinh = (tyLeSxcCoDinh || 50.0) / 100.0;
      const sxcCoDinh = cpSanXuatChung * tyLeCoDinh;
      const sxcBienDoi = cpSanXuatChung - sxcCoDinh;
      const heSoCongSuat = congSuatThucTe / congSuatDinhMuc;
      const sxcCoDinhDuocTinh = sxcCoDinh * heSoCongSuat;
      sxcDuoiCongSuat = sxcCoDinh - sxcCoDinhDuocTinh;
      cpSxcHopLy = sxcBienDoi + sxcCoDinhDuocTinh;
    }
  }

  const tongChiPhiPhatSinh = cpNvlTrucTiep + cpNhanCongTrucTiep + cpSxcHopLy;
  const tongGiaThanhZ = dDauKy + tongChiPhiPhatSinh - dCuoiKy - pheLieuThuHoi;
  const giaThanhDonViZ = tongGiaThanhZ / slHoanThanh;

  let coCau: { ty_trong_nvl?: number; ty_trong_nhan_cong?: number; ty_trong_sx_chung?: number } = {};
  if (tongChiPhiPhatSinh > 0) {
    coCau = {
      ty_trong_nvl: Number(((cpNvlTrucTiep / tongChiPhiPhatSinh) * 100).toFixed(2)),
      ty_trong_nhan_cong: Number(((cpNhanCongTrucTiep / tongChiPhiPhatSinh) * 100).toFixed(2)),
      ty_trong_sx_chung: Number(((cpSxcHopLy / tongChiPhiPhatSinh) * 100).toFixed(2)),
    };
  }

  const regimeKey = regime.toUpperCase().replace(/\s+|_/g, "");
  let cheDoStr = "Thông tư 99/2025/TT-BTC";
  let tkNhapKho = "155";
  let tenSp = "Sản phẩm";
  let butToanChiPhi: Array<any> = [];

  if (regimeKey.includes("133")) {
    cheDoStr = "Thông tư 133/2016/TT-BTC";
    tkNhapKho = "155";
    tenSp = "Thành phẩm";
    butToanChiPhi = [
      { khoan_muc: "Chi phí NVL trực tiếp", tk: "1541", so_tien: cpNvlTrucTiep },
      { khoan_muc: "Chi phí Nhân công trực tiếp", tk: "1542", so_tien: cpNhanCongTrucTiep },
      { khoan_muc: "Chi phí Sản xuất chung", tk: "1547", so_tien: cpSxcHopLy },
    ];
  } else if (regimeKey.includes("200")) {
    cheDoStr = "Thông tư 200/2014/TT-BTC";
    tkNhapKho = "1551";
    tenSp = "Thành phẩm";
    butToanChiPhi = [
      { no: "154", co: "621", so_tien: cpNvlTrucTiep },
      { no: "154", co: "622", so_tien: cpNhanCongTrucTiep },
      { no: "154", co: "627", so_tien: cpSxcHopLy },
    ];
  } else {
    cheDoStr = "Thông tư 99/2025/TT-BTC";
    tkNhapKho = "155"; // TT99 bãi bỏ tiểu khoản 1551/1557 bắt buộc
    tenSp = "Sản phẩm";
    butToanChiPhi = [
      { no: "154", co: "621", so_tien: cpNvlTrucTiep },
      { no: "154", co: "622", so_tien: cpNhanCongTrucTiep },
      { no: "154", co: "627", so_tien: cpSxcHopLy },
    ];
  }

  return {
    san_pham: productName,
    che_do_ke_toan: cheDoStr,
    so_luong_hoan_thanh: slHoanThanh,
    do_dang_dau_ky: dDauKy,
    chi_phi_phat_sinh_trong_ky: {
      nvl_truc_tiep: cpNvlTrucTiep,
      nhan_cong_truc_tiep: cpNhanCongTrucTiep,
      san_xuat_chung: cpSxcHopLy,
      tong_phat_sinh: tongChiPhiPhatSinh,
    },
    do_dang_cuoi_ky: dCuoiKy,
    phe_lieu_thu_hoi: pheLieuThuHoi,
    tong_gia_thanh_Z: tongGiaThanhZ,
    gia_thanh_don_vi_z: Number(giaThanhDonViZ.toFixed(2)),
    co_cau_chi_phi_phan_tram: coCau,
    vas02_info: {
      applied: vas02Applied,
      cong_suat_thuc_te: congSuatThucTe || null,
      cong_suat_dinh_muc: congSuatDinhMuc || null,
      sxc_duoi_cong_suat_tinh_vao_632: Number(sxcDuoiCongSuat.toFixed(2)),
    },
    but_toan_dinh_khoan: {
      tap_hop_hoac_ket_chuyen: butToanChiPhi,
      nhap_kho: {
        no: tkNhapKho,
        co: "154",
        so_tien: tongGiaThanhZ,
        dien_giai: `Nhập kho ${tenSp.toLowerCase()} ${slHoanThanh} ${productName} theo giá thành sản xuất thực tế`,
      },
    },
  };
}

export interface ProductBase {
  name: string;
  base_value: number;
}

export function allocateOverheadCosts(
  totalOverhead: number,
  products: ProductBase[],
  criteria = "nvl"
) {
  const totalBase = products.reduce((acc, p) => acc + (p.base_value || 0), 0);
  if (totalBase <= 0) {
    throw new Error("Tổng tiêu thức phân bổ phải lớn hơn 0");
  }

  const rate = totalOverhead / totalBase;
  const results = [];
  let totalAllocated = 0.0;

  for (const p of products) {
    const allocated = Number((p.base_value * rate).toFixed(2));
    totalAllocated += allocated;
    results.push({
      san_pham: p.name,
      gia_tri_tieu_thuc: p.base_value,
      he_so_phan_bo: Number(((p.base_value / totalBase) * 100).toFixed(2)),
      chi_phi_sxc_phan_bo: allocated,
    });
  }

  return {
    tong_chi_phi_sxc_can_phan_bo: totalOverhead,
    tieu_thuc_phan_bo: criteria,
    he_so_phan_bo_don_vi: rate,
    ket_qua_phan_bo: results,
    tong_da_phan_bo: Number(totalAllocated.toFixed(2)),
  };
}
