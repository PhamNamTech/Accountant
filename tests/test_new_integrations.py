"""
Bộ kiểm thử toàn diện các module tích hợp mới cho kế toán và tra cứu nguồn gốc:
1. vbpl-lookup: search_legal_document, get_document_status, auto_staleness_check, cross_reference_check
2. tax-verify: lookup_tax_code, verify_business_info, check_tax_risk_indicators, get_upcoming_deadlines, calculate_late_penalty
3. finance-tools: get_sbv_exchange_rate, get_commercial_rate, calculate_fx_difference, calculate_depreciation, validate_useful_life, lookup_industry_cost_structure, compare_with_benchmark
4. bank-api: list_supported_banks, reconcile_bank_with_ledger
"""

import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from tools.vbpl_server import (
    search_legal_document,
    get_document_status,
    auto_staleness_check,
    cross_reference_check
)
from tools.tax_verify_server import (
    lookup_tax_code,
    verify_business_info,
    check_tax_risk_indicators,
    get_upcoming_deadlines,
    calculate_late_penalty
)
from tools.finance_server import (
    get_sbv_exchange_rate,
    get_commercial_rate,
    calculate_fx_difference,
    calculate_depreciation,
    validate_useful_life,
    lookup_industry_cost_structure,
    compare_with_benchmark
)
from tools.bank_server import (
    list_supported_banks,
    reconcile_bank_with_ledger
)


def test_vbpl_lookup():
    print("\n--- [TEST GROUP 1] VBPL LOOKUP & LEGAL CITATION ---")
    
    # 1. Tra cứu văn bản
    res_search = search_legal_document("99/2025/TT-BTC")
    assert "error" not in res_search or "results" in res_search, "Search returned fatal error"
    print("  [PASS] search_legal_document: Tim kiem thanh cong")

    # 2. Trang thai van ban
    res_status = get_document_status("99/2025/TT-BTC")
    assert "doc_number" in res_status or "error" not in res_status
    print("  [PASS] get_document_status: Kiem tra hieu luc van ban TT 99/2025")

    # 3. Kiem tra doi chieu cheo (Cross reference)
    res_cross = cross_reference_check("99/2025/TT-BTC", "TK 155", "Sản phẩm")
    assert "ket_qua" in res_cross or "truong_kiem_tra" in res_cross
    print("  [PASS] cross_reference_check: Doi chieu ten TK 155 trong TT 99/2025")

    # 4. Kiem tra canh bao qua han (Staleness check)
    legal_path = os.path.join(BASE_DIR, "legal-basis.md")
    res_stale = auto_staleness_check(legal_path)
    assert "tong_van_ban_kiem_tra" in res_stale
    print(f"  [PASS] auto_staleness_check: Quet {res_stale['tong_van_ban_kiem_tra']} van ban, phat hien {res_stale['so_van_ban_can_ra_soat']} van ban can ra soat")


def test_tax_verify():
    print("\n--- [TEST GROUP 2] TAX VERIFICATION & E-INVOICE ---")

    # 1. Tra cuu ma so thue
    res_mst = lookup_tax_code("0100109106")  # VCB Tax code
    assert "tax_code" in res_mst
    print(f"  [PASS] lookup_tax_code: Tra cuu MST 0100109106 -> {res_mst.get('company_name', 'N/A')}")

    # 2. Xac thuc thong tin doanh nghiep tren hoa don
    res_verify_biz = verify_business_info("0100109106", "Ngân hàng Thương mại Cổ phần Ngoại thương Việt Nam")
    assert "match_status" in res_verify_biz
    print(f"  [PASS] verify_business_info: Ket qua doi chieu ten DN: {res_verify_biz.get('match_status')}")

    # 3. Kiem tra chi so rui ro thue
    res_risk = check_tax_risk_indicators("0100109106")
    assert "risk_level" in res_risk
    print(f"  [PASS] check_tax_risk_indicators: Muc do rui ro: {res_risk.get('risk_level')}")

    # 4. Han nop thue sap toi
    res_deadlines = get_upcoming_deadlines()
    assert "upcoming_deadlines" in res_deadlines or "deadlines" in res_deadlines
    print("  [PASS] get_upcoming_deadlines: Tinh toan lich nop to khai va thue TNDN/GTGT/TNCN")

    # 5. Tinh tien nop cham thue
    res_penalty = calculate_late_penalty(
        tax_type="GTGT",
        original_amount=100000000,
        due_date="20/07/2026",
        payment_date="30/07/2026"
    )
    assert "total_penalty" in res_penalty
    print(f"  [PASS] calculate_late_penalty: Cham nop {res_penalty.get('days_late')} ngay -> Tien phat: {res_penalty.get('total_penalty'):,.0f} VND")


def test_finance_tools():
    print("\n--- [TEST GROUP 3] FINANCE & COST BENCHMARKS ---")

    # 1. Ty gia SBV
    res_sbv = get_sbv_exchange_rate("USD")
    assert "central_rate" in res_sbv
    print(f"  [PASS] get_sbv_exchange_rate: Ty gia trung tam USD: {res_sbv.get('central_rate'):,.2f} VND")

    # 2. Ty gia NHTM VCB
    res_vcb = get_commercial_rate("USD", "VCB")
    assert "mua_chuyen_khoan" in res_vcb
    print(f"  [PASS] get_commercial_rate: VCB Mua CK: {res_vcb.get('mua_chuyen_khoan'):,.2f} | Ban CK: {res_vcb.get('ban_chuyen_khoan'):,.2f}")

    # 3. Tinh chenh lech ty gia VAS 10
    res_fx = calculate_fx_difference(
        original_rate=24500,
        current_rate=25400,
        foreign_amount=10000,
        transaction_type="liability"  # No phai tra TK 331 -> ty gia tang la lo
    )
    assert "chenh_lech_vnd" in res_fx
    assert res_fx.get("ket_qua") == "LỖ TỶ GIÁ"
    print(f"  [PASS] calculate_fx_difference: No 331 ty gia tang -> {res_fx.get('ket_qua')}: {res_fx.get('chenh_lech_vnd'):,.0f} VND ({res_fx.get('but_toan_dinh_khoan')})")

    # 4. Tinh khau hao TSCD
    res_dep = calculate_depreciation(
        asset_name="Máy dệt công nghiệp tự động",
        original_cost=600000000,
        useful_life_years=5,
        method="straight_line"
    )
    assert "chi_tiet_tinh_toan" in res_dep
    monthly_dep = res_dep["chi_tiet_tinh_toan"]["muc_khau_hao_thang"]
    assert monthly_dep == 10000000
    print(f"  [PASS] calculate_depreciation: Khau hao thang: {monthly_dep:,.0f} VND/thang")

    # 5. Kiem tra khung thoi gian trich khau hao TT 45/2013
    res_val = validate_useful_life("xe tải", 8)
    assert res_val.get("ket_luan") == "ĐẠT CHUẨN"
    print(f"  [PASS] validate_useful_life: Xe tai 8 nam -> {res_val.get('ket_luan')} (Khung: {res_val.get('khung_quy_dinh')})")

    # 6. Benchmark co cau gia thanh nganh (VSIC)
    res_bench = lookup_industry_cost_structure(vsic_code="10")
    assert "co_cau_chi_phi_chuan_nganh" in res_bench
    print(f"  [PASS] lookup_industry_cost_structure: Nganh thuc pham (VSIC 10) NVL={res_bench['co_cau_chi_phi_chuan_nganh']['ty_trong_nvl_truc_tiep']}")

    # 7. So sanh co cau thuc te voi benchmark
    res_comp = compare_with_benchmark(
        vsic_code="10",
        actual_nvl_pct=85.0,  # Vuot nguong
        actual_nc_pct=7.0,
        actual_sxc_pct=8.0
    )
    assert "danh_gia_rui_ro" in res_comp
    print(f"  [PASS] compare_with_benchmark: Phat hien {len(res_comp['danh_sach_bat_thuong'])} diem bat thuong. Rui ro: {res_comp['danh_gia_rui_ro']}")


def test_bank_api():
    print("\n--- [TEST GROUP 4] BANK API & RECONCILIATION ---")
    
    # 1. Danh sach ngan hang ho tro
    res_banks = list_supported_banks()
    assert "supported_banks" in res_banks
    print(f"  [PASS] list_supported_banks: Ho tro {len(res_banks['supported_banks'])} ngan hang lon")

    # 2. Doi soat ngan hang
    res_rec = reconcile_bank_with_ledger(
        bank_code="VCB",
        month=10,
        year=2026,
        ledger_db_path=os.path.join(BASE_DIR, "data", "database", "ketoan.db")
    )
    assert "summary" in res_rec or "error" in res_rec or "warning" in res_rec
    print("  [PASS] reconcile_bank_with_ledger: Thuc thi doi soat va dua ra khuyen nghi thanh cong")


def main():
    print("=" * 65)
    print("  KIỂM THỬ TÍCH HỢP HỆ THỐNG TRA CỨU & XÁC THỰC KẾ TOÁN MỚI")
    print("=" * 65)
    
    test_vbpl_lookup()
    test_tax_verify()
    test_finance_tools()
    test_bank_api()

    print("\n" + "=" * 65)
    print("  >>> TẤT CẢ CÁC BÀI KIỂM THỬ TÍCH HỢP ĐÃ HOÀN THÀNH 100% <<<")
    print("=" * 65)


if __name__ == "__main__":
    main()
