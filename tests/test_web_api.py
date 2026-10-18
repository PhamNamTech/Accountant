import os
import sys
from fastapi.testclient import TestClient

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
sys.stdout.reconfigure(encoding='utf-8')


from web.backend.main import app

client = TestClient(app)

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
    print(" -> PASS: /api/health")

def test_api_accounts():
    res = client.get("/api/accounts/lookup?query=112&regime=TT99")
    assert res.status_code == 200
    data = res.json()
    assert "112" in data["results"]
    assert data["results"]["112"]["name"] == "Tiền gửi không kỳ hạn"
    print(" -> PASS: /api/accounts/lookup (TT99)")

def test_api_cost_calculate():
    payload = {
        "product_name": "Bàn làm việc gỗ",
        "d_dau_ky": 2000000,
        "cp_nvl_truc_tiep": 12000000,
        "cp_nhan_cong_truc_tiep": 6000000,
        "cp_san_xuat_chung": 4000000,
        "d_cuoi_ky": 1500000,
        "sl_hoan_thanh": 10,
        "phe_lieu_thu_hoi": 500000,
        "regime": "TT99"
    }
    res = client.post("/api/cost/calculate", json=payload)
    assert res.status_code == 200
    data = res.json()
    # Z = 2tr + (12 + 6 + 4) - 1.5tr - 0.5tr = 22,000,000
    assert data["tong_gia_thanh_Z"] == 22000000.0
    assert data["gia_thanh_don_vi_z"] == 2200000.0
    print(" -> PASS: /api/cost/calculate")

def test_api_journal_entries():
    res = client.get("/api/journal/entries?limit=5")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total_records" in data
    print(f" -> PASS: /api/journal/entries (Total: {data['total_records']} rows)")

def test_api_parse_xml():
    xml_path = os.path.join(BASE_DIR, "tests", "test_data", "hoadon_01.xml")
    with open(xml_path, "rb") as f:
        res = client.post("/api/invoices/parse-xml", files={"file": ("hoadon_01.xml", f, "application/xml")})
    assert res.status_code == 200
    data = res.json()
    assert data["so_hoa_don"] == "0000015"
    print(f" -> PASS: /api/invoices/parse-xml (HĐ: {data['so_hoa_don']})")

if __name__ == "__main__":
    print("=== KIỂM THỬ WEB API FASTAPI ===")
    test_api_health()
    test_api_accounts()
    test_api_cost_calculate()
    test_api_journal_entries()
    test_api_parse_xml()
    print("=== TOÀN BỘ 5 BÀI TEST API HOÀN THÀNH XUẤT SẮC 100% ===")
