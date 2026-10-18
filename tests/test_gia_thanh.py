"""
Kịch bản kiểm thử Chuyên biệt cho Kế toán Giá thành (Cost Accounting)
1. Kiểm thử tính giá thành sản xuất (Z) và giá thành đơn vị (z) theo Thông tư 200/133.
2. Kiểm thử phân bổ chi phí sản xuất chung (TK 627) theo tiêu thức NVL / Nhân công.
3. Kiểm thử xuất file Excel 'THẺ TÍNH GIÁ THÀNH SẢN PHẨM' tự động.
"""

import os
import sys

BASE_DIR = os.path.abspath("F:/Accountant")
sys.path.insert(0, BASE_DIR)

from tools.ketoan_server import (
    calculate_product_cost,
    allocate_overhead_costs,
    export_cost_sheet_excel
)

def test_cost_calculation():
    print("[TEST GIA THANH 1] Tính giá thành sản phẩm phương pháp Giản đơn...")
    res = calculate_product_cost(
        product_name="Bàn làm việc gỗ công nghiệp MDF",
        d_dau_ky=10000000.0,
        cp_nvl_truc_tiep=50000000.0,
        cp_nhan_cong_truc_tiep=20000000.0,
        cp_san_xuat_chung=15000000.0,
        d_cuoi_ky=5000000.0,
        sl_hoan_thanh=100,
        phe_lieu_thu_hoi=1000000.0
    )

    # Z = 10,000,000 + 85,000,000 - 5,000,000 - 1,000,000 = 89,000,000
    assert res["tong_gia_thanh_Z"] == 89000000.0, f"Tổng giá thành sai: {res['tong_gia_thanh_Z']}"
    # z = 890,000 đ
    assert res["gia_thanh_don_vi_z"] == 890000.0, f"Giá thành đơn vị sai: {res['gia_thanh_don_vi_z']}"
    
    print(f" -> Đạt: Tổng giá thành Z = {res['tong_gia_thanh_Z']:,.0f} VND")
    print(f"    Giá thành đơn vị z = {res['gia_thanh_don_vi_z']:,.0f} VND/sản phẩm (100 SP hoàn thành)")
    print(f"    Cơ cấu chi phí: NVL: {res['co_cau_chi_phi_phan_tram']['ty_trong_nvl']}% | "
          f"Nhân công: {res['co_cau_chi_phi_phan_tram']['ty_trong_nhan_cong']}% | "
          f"SXC: {res['co_cau_chi_phi_phan_tram']['ty_trong_sx_chung']}%")
    print("    Bút toán nhập kho:", res["but_toan_dinh_khoan"]["nhap_kho"])

def test_overhead_allocation():
    print("\n[TEST GIA THANH 2] Phân bổ chi phí sản xuất chung (TK 627)...")
    total_overhead = 18000000.0 # 18 triệu tiền điện, khấu hao, quản lý xưởng
    products = [
        {"name": "Bàn làm việc MDF", "base_value": 50000000.0}, # NVL 50tr
        {"name": "Ghế văn phòng lưới", "base_value": 25000000.0}, # NVL 25tr
        {"name": "Tủ tài liệu hồ sơ", "base_value": 15000000.0}   # NVL 15tr
    ]
    # Tổng NVL = 90tr -> Tỷ lệ: Bàn: 55.56%, Ghế: 27.78%, Tủ: 16.67%
    res = allocate_overhead_costs(total_overhead, products, criteria="nvl")
    assert round(res["tong_da_phan_bo"]) == 18000000, "Tổng phân bổ không khớp!"
    
    print(f" -> Đạt: Đã phân bổ {total_overhead:,.0f} VND chi phí SXC cho 3 sản phẩm:")
    for p in res["ket_qua_phan_bo"]:
        print(f"    * {p['san_pham']}: {p['chi_phi_sxc_phan_bo']:,.0f} VND ({p['he_so_phan_bo']}%)")

def test_export_cost_sheet():
    print("\n[TEST GIA THANH 3] Xuất Thẻ tính giá thành sản phẩm ra Excel...")
    out_path = os.path.join(BASE_DIR, "tests", "test_output", "The_Tinh_Gia_Thanh_Ban_MDF.xlsx")
    
    res = export_cost_sheet_excel(
        output_excel_path=out_path,
        product_name="Bàn làm việc gỗ MDF",
        ky_tinh_gia_thanh="Tháng 10/2026",
        sl_hoan_thanh=100,
        d_dau_ky_dict={"nvl": 6000000, "nc": 2500000, "sxc": 1500000},
        phat_sinh_dict={"nvl": 50000000, "nc": 20000000, "sxc": 15000000},
        d_cuoi_ky_dict={"nvl": 3000000, "nc": 1200000, "sxc": 800000}
    )

    assert res["status"] == "success", "Lỗi xuất file Excel Thẻ tính giá thành!"
    assert os.path.exists(out_path), "File Thẻ tính giá thành không tồn tại!"
    print(f" -> Đạt: Đã tạo file Thẻ tính giá thành chuẩn mẫu tại: {out_path}")

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print("==================================================")
    print(" BẮT ĐẦU KIỂM THỬ MODULE KẾ TOÁN GIÁ THÀNH")
    print("==================================================")
    test_cost_calculation()
    test_overhead_allocation()
    test_export_cost_sheet()
    print("\n==================================================")
    print(" KIỂM THỬ KẾ TOÁN GIÁ THÀNH HOÀN TẤT THÀNH CÔNG 100%!")
    print("==================================================")
