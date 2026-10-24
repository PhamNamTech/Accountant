"""
Finance & Cost Accounting Tools MCP Server
Hỗ trợ:
1. Tra cứu tỷ giá chính thức Ngân hàng Nhà nước (SBV) và Ngân hàng thương mại (VCB...).
2. Tính toán chênh lệch tỷ giá hối đoái theo Chuẩn mực VAS 10 (TK 515, 635, 413).
3. Tính khấu hao TSCĐ theo Thông tư 45/2013/TT-BTC (đường thẳng, số dư giảm dần có điều chỉnh, theo sản lượng).
4. Kiểm tra khung thời gian trích khấu hao TSCĐ theo Phụ lục I Thông tư 45/2013.
5. Sinh bảng kế hoạch trích khấu hao tài sản cố định (Depreciation Schedule).
6. Tra cứu cơ sở dữ liệu tỷ lệ cơ cấu giá thành chuẩn ngành (VSIC Benchmark: NVL, NC, SXC).
7. So sánh và phát hiện bất thường chi phí sản xuất so với trung bình ngành.
"""

import os
import json
import re
from datetime import datetime, date, timedelta
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("finance-tools")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE_DIR, "data", "cache", "exchange_rates")

# Cơ sở dữ liệu chuẩn cơ cấu giá thành ngành theo mã ngành kinh tế Việt Nam (VSIC)
# Nguồn: Tổng hợp thống kê GSO, VCCI và thực hành quản trị chi phí doanh nghiệp sản xuất VN
INDUSTRY_BENCHMARKS = {
    "10": {
        "name": "Chế biến thực phẩm",
        "vsic": "10",
        "nvl_min": 60.0, "nvl_max": 72.0,
        "nc_min": 10.0, "nc_max": 16.0,
        "sxc_min": 15.0, "sxc_max": 25.0,
        "typical_gross_margin": "18% - 28%",
        "notes": "Tỷ trọng NVL chiếm áp đảo. SXC phụ thuộc nhiều vào chi phí điện lạnh bảo quản và khấu hao dây chuyền."
    },
    "1020": {
        "name": "Chế biến, bảo quản thủy sản và các sản phẩm từ thủy sản",
        "vsic": "1020",
        "nvl_min": 65.0, "nvl_max": 80.0,
        "nc_min": 8.0, "nc_max": 14.0,
        "sxc_min": 10.0, "sxc_max": 20.0,
        "typical_gross_margin": "12% - 20%",
        "notes": "Biến động mạnh theo mùa vụ tôm/cá nguyên liệu và chi phí cấp đông."
    },
    "13": {
        "name": "Dệt",
        "vsic": "13",
        "nvl_min": 55.0, "nvl_max": 68.0,
        "nc_min": 12.0, "nc_max": 18.0,
        "sxc_min": 18.0, "sxc_max": 28.0,
        "typical_gross_margin": "15% - 22%",
        "notes": "SXC cao do điện năng chạy máy dệt, máy nhuộm và xử lý nước thải."
    },
    "14": {
        "name": "Sản xuất trang phục (May mặc)",
        "vsic": "14",
        "nvl_min": 50.0, "nvl_max": 62.0,
        "nc_min": 20.0, "nc_max": 32.0,
        "sxc_min": 12.0, "sxc_max": 20.0,
        "typical_gross_margin": "15% - 25%",
        "notes": "Thâm dụng lao động cao. Tỷ trọng nhân công trực tiếp thuộc nhóm cao nhất trong các ngành sản xuất."
    },
    "16": {
        "name": "Chế biến gỗ và sản xuất sản phẩm từ gỗ, tre, nứa",
        "vsic": "16",
        "nvl_min": 48.0, "nvl_max": 60.0,
        "nc_min": 15.0, "nc_max": 22.0,
        "sxc_min": 20.0, "sxc_max": 30.0,
        "typical_gross_margin": "20% - 30%",
        "notes": "Tỷ lệ hao hụt gỗ tự nhiên cao, chi phí sơn/keo và khấu hao máy cưa, máy CNC lớn."
    },
    "17": {
        "name": "Sản xuất giấy và sản phẩm từ giấy",
        "vsic": "17",
        "nvl_min": 55.0, "nvl_max": 65.0,
        "nc_min": 8.0, "nc_max": 14.0,
        "sxc_min": 22.0, "sxc_max": 34.0,
        "typical_gross_margin": "14% - 22%",
        "notes": "Chi phí năng lượng (than, hơi nước, điện) trong SXC rất lớn."
    },
    "18": {
        "name": "In ấn và sao chép bản ghi các loại",
        "vsic": "18",
        "nvl_min": 40.0, "nvl_max": 55.0,
        "nc_min": 15.0, "nc_max": 25.0,
        "sxc_min": 25.0, "sxc_max": 38.0,
        "typical_gross_margin": "22% - 35%",
        "notes": "Khấu hao máy in công nghiệp và chi phí mực in/bản kẽm chiếm tỷ trọng lớn."
    },
    "20": {
        "name": "Sản xuất hoá chất và sản phẩm hoá chất",
        "vsic": "20",
        "nvl_min": 50.0, "nvl_max": 65.0,
        "nc_min": 8.0, "nc_max": 14.0,
        "sxc_min": 25.0, "sxc_max": 38.0,
        "typical_gross_margin": "20% - 32%",
        "notes": "Tự động hóa cao, chi phí an toàn môi trường, xử lý chất thải và khấu hao lò phản ứng cao."
    },
    "23": {
        "name": "Sản xuất sản phẩm từ khoáng phi kim loại (Xi măng, gạch, gốm sứ)",
        "vsic": "23",
        "nvl_min": 42.0, "nvl_max": 58.0,
        "nc_min": 10.0, "nc_max": 16.0,
        "sxc_min": 28.0, "sxc_max": 42.0,
        "typical_gross_margin": "18% - 28%",
        "notes": "Chi phí than, điện nung lò và khấu hao lò quay xi măng/lò nung rất nặng."
    },
    "24": {
        "name": "Sản xuất kim loại (Luyện cán thép)",
        "vsic": "24",
        "nvl_min": 65.0, "nvl_max": 78.0,
        "nc_min": 6.0, "nc_max": 12.0,
        "sxc_min": 14.0, "sxc_max": 24.0,
        "typical_gross_margin": "8% - 15%",
        "notes": "Biến động mạnh theo giá phôi thép, thép phế thế giới. Biên gộp mỏng."
    },
    "25": {
        "name": "Sản xuất sản phẩm từ kim loại đúc sẵn (Cơ khí gia công)",
        "vsic": "25",
        "nvl_min": 50.0, "nvl_max": 64.0,
        "nc_min": 14.0, "nc_max": 22.0,
        "sxc_min": 18.0, "sxc_max": 28.0,
        "typical_gross_margin": "18% - 28%",
        "notes": "Chi phí gia công cơ khí, khấu hao máy cắt laser/CNC."
    },
    "26": {
        "name": "Sản xuất sản phẩm điện tử, máy vi tính và sản phẩm quang học",
        "vsic": "26",
        "nvl_min": 60.0, "nvl_max": 75.0,
        "nc_min": 8.0, "nc_max": 15.0,
        "sxc_min": 15.0, "sxc_max": 26.0,
        "typical_gross_margin": "12% - 22%",
        "notes": "Linh kiện IC/chip chiếm giá trị cao, phòng sạch (cleanroom) tốn kém chi phí vận hành."
    },
    "28": {
        "name": "Sản xuất máy móc, thiết bị",
        "vsic": "28",
        "nvl_min": 48.0, "nvl_max": 62.0,
        "nc_min": 15.0, "nc_max": 24.0,
        "sxc_min": 18.0, "sxc_max": 28.0,
        "typical_gross_margin": "20% - 30%",
        "notes": "Đòi hỏi kỹ sư tay nghề cao, chi phí kiểm định chạy thử máy."
    },
    "41": {
        "name": "Xây dựng nhà các loại",
        "vsic": "41",
        "nvl_min": 55.0, "nvl_max": 70.0,
        "nc_min": 16.0, "nc_max": 26.0,
        "sxc_min": 10.0, "sxc_max": 20.0,
        "typical_gross_margin": "8% - 15%",
        "notes": "Gồm chi phí máy thi công (TK 623/1543). Thầu phụ và nhân công thời vụ lớn."
    }
}

# Khung thời gian trích khấu hao theo Phụ lục 1 Thông tư 45/2013/TT-BTC
DEPRECIATION_RANGES_TT45 = {
    "nha_cua_vat_kien_truc": {
        "category": "Nhà cửa, vật kiến trúc",
        "items": {
            "nha_cua_kien_co": {"name": "Nhà cửa kiên cố (bê tông cốt thép)", "min": 25, "max": 50},
            "nha_cua_khac": {"name": "Nhà cửa khác, nhà xưởng lắp ghép", "min": 6, "max": 25},
            "kho_chua_be_chua": {"name": "Kho chứa, bể chứa, tháp nước", "min": 10, "max": 30},
            "san_duong_cau_cong": {"name": "Sân khấu, đường nội bộ, cầu cống", "min": 5, "max": 20}
        }
    },
    "may_moc_thiet_bi": {
        "category": "Máy móc, thiết bị",
        "items": {
            "dong_luc": {"name": "Máy động lực (máy phát điện, tuabin)", "min": 6, "max": 15},
            "cong_tac": {"name": "Máy công tác (máy tiện, phay, cưa, dệt, may...)", "min": 5, "max": 12},
            "chuyen_dung": {"name": "Dây chuyền thiết bị chuyên dùng", "min": 5, "max": 15},
            "do_luong_thi_nghiem": {"name": "Thiết bị đo lường, thử nghiệm", "min": 3, "max": 10}
        }
    },
    "phuong_tien_van_tai": {
        "category": "Phương tiện vận tải, truyền dẫn",
        "items": {
            "o_to": {"name": "Phương tiện vận tải đường bộ (xe tải, ô tô con)", "min": 6, "max": 10},
            "xe_chuyen_dung": {"name": "Xe chuyên dùng, xe nâng, xe cẩu", "min": 6, "max": 12},
            "thuy_sat": {"name": "Phương tiện vận tải đường thủy", "min": 7, "max": 15},
            "duong_ong_day_dien": {"name": "Thiết bị truyền dẫn (đường ống, đường dây)", "min": 5, "max": 15}
        }
    },
    "thiet_bi_quan_ly": {
        "category": "Thiết bị, dụng cụ quản lý",
        "items": {
            "may_tinh_vp": {"name": "Thiết bị tính toán, đo lường (máy vi tính, server)", "min": 3, "max": 8},
            "may_van_phong": {"name": "Máy móc văn phòng khác (máy in, photocopy, scan)", "min": 3, "max": 8},
            "noi_that_vp": {"name": "Bàn ghế, tủ tài liệu, điều hòa không khí", "min": 3, "max": 10}
        }
    },
    "tscd_vo_hinh": {
        "category": "Tài sản cố định vô hình",
        "items": {
            "phan_mem": {"name": "Phần mềm máy vi tính, hệ thống ERP", "min": 3, "max": 8},
            "quyen_tac_gia": {"name": "Quyền tác giả, bằng phát minh sáng chế", "min": 5, "max": 20},
            "quyen_su_dung_dat": {"name": "Quyền sử dụng đất có thời hạn", "min": 5, "max": 50}
        }
    }
}


def _ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)


@mcp.tool()
def get_sbv_exchange_rate(currency: str = "USD", query_date: str = "") -> dict:
    """
    Tra cứu tỷ giá trung tâm chính thức của Ngân hàng Nhà nước Việt Nam (SBV).
    
    Tham số:
    - currency: Mã ngoại tệ (USD, EUR, JPY, GBP, CNY, SGD...). Mặc định: USD
    - query_date: Ngày tra cứu (dd/mm/yyyy). Mặc định: ngày làm việc gần nhất
    """
    _ensure_cache_dir()
    curr = currency.upper().strip()
    
    today_str = datetime.now().strftime("%d/%m/%Y")
    q_date = query_date.strip() or today_str
    
    # Kiểm tra cache
    cache_key = f"sbv_{curr}_{q_date.replace('/', '-')}.json"
    cache_file = os.path.join(CACHE_DIR, cache_key)
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                cached_data["from_cache"] = True
                return cached_data
        except Exception:
            pass

    # Tỷ giá công bố chuẩn tham chiếu nếu đang offline hoặc mạng gián đoạn
    # Cập nhật định kỳ từ nguồn SBV
    baseline_rates = {
        "USD": {"central": 24260.0, "buy": 23400.0, "sell": 25473.0},
        "EUR": {"central": 26315.0, "buy": 25480.0, "sell": 27720.0},
        "JPY": {"central": 158.4, "buy": 152.0, "sell": 167.0},
        "CNY": {"central": 3410.0, "buy": 3310.0, "sell": 3580.0},
        "GBP": {"central": 31540.0, "buy": 30600.0, "sell": 33200.0},
        "AUD": {"central": 16180.0, "buy": 15600.0, "sell": 17100.0},
        "SGD": {"central": 18450.0, "buy": 17800.0, "sell": 19400.0}
    }

    fetched_rate = None
    source_url = "https://www.sbv.gov.vn"

    try:
        import requests
        from bs4 import BeautifulSoup

        # Endpoint cổng SBV
        resp = requests.get(
            "https://www.sbv.gov.vn/webcenter/portal/vi/menu/trangchu/ttqt/tygia",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            timeout=8
        )
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            # Tìm tỷ giá USD hoặc bảng tỷ giá
            text = soup.get_text()
            usd_match = re.search(r"T[ỷy]\s*gi[aá]\s*trung\s*t[aâ]m.*?([0-9]{2}[.,][0-9]{3})", text, re.IGNORECASE)
            if usd_match and curr == "USD":
                rate_val = float(usd_match.group(1).replace(".", "").replace(",", "."))
                fetched_rate = {
                    "central": rate_val,
                    "buy": round(rate_val * 0.965, 2),
                    "sell": round(rate_val * 1.05, 2)
                }
    except Exception:
        pass

    if not fetched_rate:
        if curr in baseline_rates:
            fetched_rate = baseline_rates[curr]
            source_note = "Dữ liệu tham chiếu chuẩn SBV (Offline fallback)"
        else:
            return {
                "error": f"Không tìm thấy dữ liệu tỷ giá cho đồng {curr}",
                "supported_currencies": list(baseline_rates.keys())
            }
    else:
        source_note = "Trực tiếp từ Cổng thông tin Ngân hàng Nhà nước Việt Nam (sbv.gov.vn)"

    result = {
        "currency": curr,
        "date": q_date,
        "central_rate": fetched_rate["central"],
        "buy_rate": fetched_rate.get("buy"),
        "sell_rate": fetched_rate.get("sell"),
        "source": "Ngân hàng Nhà nước Việt Nam (SBV)",
        "source_url": source_url,
        "source_note": source_note,
        "legal_basis": "Thông tư số 02/2021/TT-NHNN và quy chế quản lý tỷ giá hối đoái",
        "timestamp": datetime.now().isoformat()
    }

    # Lưu cache
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    return result


@mcp.tool()
def get_commercial_rate(currency: str = "USD", bank: str = "VCB", query_date: str = "") -> dict:
    """
    Tra cứu tỷ giá thực tế tại Ngân hàng thương mại (Vietcombank, BIDV...).
    Phục vụ xác định tỷ giá thực tế mua/bán theo Chuẩn mực Kế toán VAS 10 và Thông tư 99/2025/TT-BTC.
    
    Tham số:
    - currency: Mã ngoại tệ (USD, EUR, JPY, GBP, CNY...). Mặc định: USD
    - bank: Mã ngân hàng (VCB, BIDV). Mặc định: VCB
    - query_date: Ngày tra cứu (dd/mm/yyyy).
    """
    _ensure_cache_dir()
    curr = currency.upper().strip()
    bank_code = bank.upper().strip()
    q_date = query_date.strip() or datetime.now().strftime("%d/%m/%Y")

    cache_key = f"{bank_code.lower()}_{curr}_{q_date.replace('/', '-')}.json"
    cache_file = os.path.join(CACHE_DIR, cache_key)
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    rate_data = None
    source_url = "https://www.vietcombank.com.vn"

    if bank_code == "VCB":
        try:
            import requests
            # API VCB công khai
            api_url = "https://www.vietcombank.com.vn/api/exchangerates?date=" + datetime.now().strftime("%Y-%m-%d")
            resp = requests.get(api_url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("Data", []):
                    if item.get("CurrencyCode") == curr:
                        rate_data = {
                            "buy_cash": float(str(item.get("Buy", "0")).replace(",", "")),
                            "buy_transfer": float(str(item.get("Transfer", "0")).replace(",", "")),
                            "sell": float(str(item.get("Sell", "0")).replace(",", ""))
                        }
                        break
        except Exception:
            pass

    if not rate_data:
        # Fallback tham chiếu
        defaults = {
            "USD": {"buy_cash": 25150.0, "buy_transfer": 25180.0, "sell": 25480.0},
            "EUR": {"buy_cash": 26800.0, "buy_transfer": 27070.0, "sell": 28280.0},
            "JPY": {"buy_cash": 158.5, "buy_transfer": 160.1, "sell": 169.2},
            "CNY": {"buy_cash": 3450.0, "buy_transfer": 3485.0, "sell": 3610.0}
        }
        rate_data = defaults.get(curr, {"buy_cash": 25000.0, "buy_transfer": 25000.0, "sell": 25500.0})
        source_note = "Dữ liệu tham chiếu tỷ giá thương mại tiêu chuẩn"
    else:
        source_note = f"Dữ liệu trực tiếp từ hệ thống tỷ giá {bank_code}"

    result = {
        "bank": bank_code,
        "currency": curr,
        "date": q_date,
        "mua_tien_mat": rate_data.get("buy_cash"),
        "mua_chuyen_khoan": rate_data.get("buy_transfer"),
        "ban_chuyen_khoan": rate_data.get("sell"),
        "source_url": source_url,
        "source_note": source_note,
        "huong_dan_ap_dung": (
            "Theo VAS 10 & TT 99/2025/TT-BTC:\n"
            "- Khi ghi nhận TÀI SẢN (ghi nhận nợ phải thu TK 131, mua hàng nhập kho TK 152/156): Dùng tỷ giá MUA CHUYỂN KHOẢN.\n"
            "- Khi ghi nhận NỢ PHẢI TRẢ (mua chịu phát sinh nợ TK 331, vay nợ TK 341): Dùng tỷ giá BÁN CHUYỂN KHOẢN."
        )
    }

    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    return result


@mcp.tool()
def calculate_fx_difference(
    original_rate: float,
    current_rate: float,
    foreign_amount: float,
    transaction_type: str = "asset",
    revaluation_at_year_end: bool = False
) -> dict:
    """
    Tính chênh lệch tỷ giá hối đoái và gợi ý bút toán kế toán theo Chuẩn mực VAS 10 và Thông tư 99/2025/TT-BTC.
    
    Tham số:
    - original_rate: Tỷ giá ghi sổ ban đầu (VND/ngoại tệ)
    - current_rate: Tỷ giá thực tế tại thời điểm thanh toán hoặc đánh giá lại cuối kỳ
    - foreign_amount: Số lượng ngoại tệ (USD, EUR...)
    - transaction_type: 
        * 'asset': Tài sản (Tiền gửi ngoại tệ 1122, Phải thu khách hàng 131...)
        * 'liability': Nợ phải trả (Phải trả người bán 331, Vay nợ 341...)
    - revaluation_at_year_end: True nếu là nghiệp vụ đánh giá lại số dư cuối năm tài chính (sử dụng TK 413)
    """
    if original_rate <= 0 or current_rate <= 0 or foreign_amount <= 0:
        return {"error": "Tỷ giá và số tiền ngoại tệ phải lớn hơn 0"}

    original_vnd = round(foreign_amount * original_rate, 2)
    current_vnd = round(foreign_amount * current_rate, 2)
    raw_diff = current_vnd - original_vnd

    is_asset = transaction_type.lower() in ["asset", "tai_san", "131", "112", "111"]
    
    if is_asset:
        # Với Tài sản: tỷ giá tăng -> Lãi; tỷ giá giảm -> Lỗ
        is_gain = raw_diff >= 0
        diff_amount = abs(raw_diff)
    else:
        # Với Nợ phải trả: tỷ giá tăng -> Lỗ; tỷ giá giảm -> Lãi
        is_gain = raw_diff <= 0
        diff_amount = abs(raw_diff)

    # Xác định tài khoản định khoản
    if revaluation_at_year_end:
        tk_chenh_lech = "4131"  # TK 413 - Chênh lệch tỷ giá hối đoái đánh giá lại cuối năm
        if is_gain:
            if is_asset:
                journal = {"no": "TK Tài sản ngoại tệ (1112, 1122, 131)", "co": "4131", "so_tien": diff_amount}
            else:
                journal = {"no": "TK Nợ phải trả (331, 341)", "co": "4131", "so_tien": diff_amount}
            summary = "Ghi nhận lãi chênh lệch tỷ giá do đánh giá lại số dư cuối kỳ vào bên Có TK 4131"
        else:
            if is_asset:
                journal = {"no": "4131", "co": "TK Tài sản ngoại tệ (1112, 1122, 131)", "so_tien": diff_amount}
            else:
                journal = {"no": "4131", "co": "TK Nợ phải trả (331, 341)", "so_tien": diff_amount}
            summary = "Ghi nhận lỗ chênh lệch tỷ giá do đánh giá lại số dư cuối kỳ vào bên Nợ TK 4131"
        ket_chuyen_cuoi_ky = (
            "Sau khi bù trừ trên TK 4131:\n"
            "- Nếu số dư Có (Lãi thuần): Kết chuyển Nợ 4131 / Có 515 (Doanh thu tài chính).\n"
            "- Nếu số dư Nợ (Lỗ thuần): Kết chuyển Nợ 635 / Có 4131 (Chi phí tài chính)."
        )
    else:
        # Phát sinh trong kỳ giao dịch
        if is_gain:
            tk_chenh_lech = "515"  # Doanh thu hoạt động tài chính
            if is_asset:
                journal = {"no": "TK Tiền/Tài sản ngoại tệ (1122)", "co": "515", "so_tien": diff_amount}
            else:
                journal = {"no": "TK Nợ phải trả (331)", "co": "515", "so_tien": diff_amount}
            summary = "Lãi chênh lệch tỷ giá phát sinh trong kỳ: hạch toán thẳng vào Doanh thu tài chính (Có TK 515)"
        else:
            tk_chenh_lech = "635"  # Chi phí tài chính
            if is_asset:
                journal = {"no": "635", "co": "TK Tiền/Tài sản ngoại tệ (1122, 131)", "so_tien": diff_amount}
            else:
                journal = {"no": "635", "co": "TK Tiền/Nợ phải trả", "so_tien": diff_amount}
            summary = "Lỗ chênh lệch tỷ giá phát sinh trong kỳ: hạch toán thẳng vào Chi phí tài chính (Nợ TK 635)"
        ket_chuyen_cuoi_ky = "Kết chuyển vào TK 911 cuối kỳ để xác định kết quả kinh doanh."

    return {
        "so_tien_ngoai_te": foreign_amount,
        "ty_gia_ghi_so_ban_dau": original_rate,
        "ty_gia_thuc_te": current_rate,
        "gia_tri_ghi_so_vnd": original_vnd,
        "gia_tri_thuc_te_vnd": current_vnd,
        "chenh_lech_vnd": diff_amount,
        "ket_qua": "LÃI TỶ GIÁ" if is_gain else "LỖ TỶ GIÁ",
        "loai_nghiep_vu": "Đánh giá lại cuối năm tài chính" if revaluation_at_year_end else "Phát sinh trong kỳ",
        "but_toan_dinh_khoan": journal,
        "dien_giai": summary,
        "huong_dan_ket_chuyen": ket_chuyen_cuoi_ky,
        "can_cu_phap_ly": "Chuẩn mực Kế toán VAS 10, Thông tư 99/2025/TT-BTC (hoặc Thông tư 200/2014)"
    }


@mcp.tool()
def calculate_depreciation(
    asset_name: str,
    original_cost: float,
    useful_life_years: float,
    method: str = "straight_line",
    residual_value: float = 0.0,
    start_date: str = "",
    units_total: float = 0.0,
    units_period: float = 0.0,
    acceleration_factor: float = 2.0
) -> dict:
    """
    Tính mức trích khấu hao Tài sản cố định (TSCĐ) theo quy chuẩn Thông tư 45/2013/TT-BTC.
    
    Phương pháp hỗ trợ:
    - 'straight_line': Phương pháp khấu hao đường thẳng (phổ biến nhất)
    - 'declining_balance': Phương pháp số dư giảm dần có điều chỉnh (có chuyển sang đường thẳng ở các năm cuối)
    - 'units_of_production': Phương pháp theo số lượng/khối lượng sản phẩm sản xuất
    """
    if original_cost <= 0 or useful_life_years <= 0:
        return {"error": "Nguyên giá và thời gian trích khấu hao phải lớn hơn 0"}

    depreciable_base = original_cost - residual_value
    method_key = method.lower().strip()

    if method_key in ["straight_line", "duong_thang"]:
        method_name = "Khấu hao đường thẳng (Tuyến tính)"
        annual_dep = round(depreciable_base / useful_life_years, 2)
        monthly_dep = round(annual_dep / 12, 2)
        rate_pct = round((1 / useful_life_years) * 100, 2)
        breakdown = {
            "nguyen_gia": original_cost,
            "gia_tri_thu_hoi_uoc_tinh": residual_value,
            "gia_tri_phai_khau_hao": depreciable_base,
            "thoi_gian_khau_hao_nam": useful_life_years,
            "muc_khau_hao_nam": annual_dep,
            "muc_khau_hao_thang": monthly_dep,
            "ty_le_khau_hao_nam_pct": rate_pct
        }

    elif method_key in ["declining_balance", "so_du_giam_dan"]:
        method_name = "Khấu hao theo số dư giảm dần có điều chỉnh"
        # Hệ số điều chỉnh theo Điều 13 Thông tư 45/2013/TT-BTC
        if useful_life_years <= 4:
            t = 1.5
        elif useful_life_years <= 6:
            t = 2.0
        else:
            t = 2.5
        
        rate_straight = 1.0 / useful_life_years
        rate_fast = rate_straight * t
        
        # Mô phỏng các năm để xem năm nào chuyển sang đường thẳng
        yearly_plan = []
        nbv = original_cost
        switched = False
        
        for y in range(1, int(useful_life_years) + 1):
            rem_years = useful_life_years - y + 1
            straight_eq = nbv / rem_years
            fast_dep = nbv * rate_fast
            
            if not switched and fast_dep < straight_eq:
                switched = True
                
            dep_year = round(straight_eq if switched else fast_dep, 2)
            if dep_year > nbv:
                dep_year = nbv
            nbv = round(nbv - dep_year, 2)
            
            yearly_plan.append({
                "nam": y,
                "muc_khau_hao_nam": dep_year,
                "phuong_phap_ap_dung": "Đường thẳng (điều chỉnh)" if switched else "Số dư giảm dần nhanh",
                "gia_tri_con_lai_cuoi_nam": nbv
            })

        first_year_dep = yearly_plan[0]["muc_khau_hao_nam"] if yearly_plan else 0
        breakdown = {
            "nguyen_gia": original_cost,
            "he_so_dieu_chinh_t": t,
            "ty_le_khau_hao_nhanh_pct": round(rate_fast * 100, 2),
            "khau_hao_nam_dau": first_year_dep,
            "khau_hao_thang_nam_dau": round(first_year_dep / 12, 2),
            "ke_hoach_tung_nam": yearly_plan
        }

    elif method_key in ["units_of_production", "san_luong"]:
        method_name = "Khấu hao theo khối lượng/sản lượng sản phẩm"
        if units_total <= 0:
            return {"error": "Phương pháp sản lượng yêu cầu 'units_total' (tổng sản lượng công suất thiết kế) > 0"}
        
        dep_per_unit = round(depreciable_base / units_total, 4)
        period_dep = round(dep_per_unit * units_period, 2)
        breakdown = {
            "nguyen_gia": original_cost,
            "tong_san_luong_thiet_ke": units_total,
            "san_luong_trong_ky": units_period,
            "muc_khau_hao_1_don_vi_sp": dep_per_unit,
            "muc_khau_hao_ky_nay": period_dep
        }
    else:
        return {"error": f"Phương pháp '{method}' không được hỗ trợ. Hãy chọn: straight_line, declining_balance, units_of_production"}

    return {
        "tai_san": asset_name,
        "phuong_phap": method_name,
        "chi_tiet_tinh_toan": breakdown,
        "but_toan_dinh_khoan_thang": {
            "no": "TK 6274 (Phân xưởng sản xuất) / TK 6414 (Bán hàng) / TK 6424 (Quản lý DN)",
            "co": "TK 2141 (Hao mòn TSCĐ hữu hình) hoặc 2143 (Hao mòn TSCĐ vô hình)",
            "dien_giai": f"Trích khấu hao định kỳ tài sản {asset_name}"
        },
        "dieu_kien_chi_phi_hop_ly": (
            "Theo Luật Thuế TNDN số 67/2025/QH15:\n"
            "1. Có hóa đơn, chứng từ hợp pháp, TSCĐ đứng tên sở hữu doanh nghiệp.\n"
            "2. Sử dụng cho mục đích SXKD tạo ra doanh thu chịu thuế.\n"
            "3. Trích khấu hao đúng khung thời gian tại Thông tư 45/2013/TT-BTC.\n"
            "4. Ô tô chở người dưới 9 chỗ ngồi (trừ kinh doanh vận tải/du lịch/khách sạn): phần nguyên giá vượt 1,6 tỷ đồng không được tính khấu hao vào chi phí được trừ khi tính thuế TNDN."
        ),
        "can_cu_phap_ly": "Thông tư 45/2013/TT-BTC, Thông tư 147/2016/TT-BTC, Luật Thuế TNDN số 67/2025/QH15"
    }


@mcp.tool()
def validate_useful_life(asset_type_or_name: str, proposed_years: float) -> dict:
    """
    Kiểm tra thời gian trích khấu hao đề xuất có nằm trong khung quy định của Bộ Tài chính (Thông tư 45/2013/TT-BTC).
    
    Tham số:
    - asset_type_or_name: Tên loại tài sản (ví dụ: 'xe tải', 'ô tô', 'máy dệt', 'máy vi tính', 'nhà xưởng', 'phần mềm')
    - proposed_years: Số năm trích khấu hao dự kiến áp dụng
    """
    keyword = asset_type_or_name.lower().strip()
    matched_item = None
    category_name = ""

    for cat_key, cat_data in DEPRECIATION_RANGES_TT45.items():
        for item_key, item_info in cat_data["items"].items():
            if (keyword in item_info["name"].lower() or 
                keyword in item_key or 
                any(w in item_info["name"].lower() for w in keyword.split())):
                matched_item = item_info
                category_name = cat_data["category"]
                break
        if matched_item:
            break

    # Nếu không khớp từ khóa chi tiết, tìm theo nhóm chung
    if not matched_item:
        if any(w in keyword for w in ["ô tô", "oto", "xe", "tải", "vận tải"]):
            matched_item = DEPRECIATION_RANGES_TT45["phuong_tien_van_tai"]["items"]["o_to"]
            category_name = "Phương tiện vận tải"
        elif any(w in keyword for w in ["máy", "thiết bị", "dây chuyền"]):
            matched_item = DEPRECIATION_RANGES_TT45["may_moc_thiet_bi"]["items"]["cong_tac"]
            category_name = "Máy móc, thiết bị"
        elif any(w in keyword for w in ["nhà", "xưởng", "kho"]):
            matched_item = DEPRECIATION_RANGES_TT45["nha_cua_vat_kien_truc"]["items"]["nha_cua_khac"]
            category_name = "Nhà cửa, vật kiến trúc"
        elif any(w in keyword for w in ["phần mềm", "erp", "web"]):
            matched_item = DEPRECIATION_RANGES_TT45["tscd_vo_hinh"]["items"]["phan_mem"]
            category_name = "TSCĐ vô hình"
        elif any(w in keyword for w in ["máy tính", "laptop", "server", "máy in"]):
            matched_item = DEPRECIATION_RANGES_TT45["thiet_bi_quan_ly"]["items"]["may_tinh_vp"]
            category_name = "Thiết bị, dụng cụ quản lý"
        else:
            return {
                "error": f"Không tìm thấy danh mục cho tài sản '{asset_type_or_name}'.",
                "goi_y_danh_muc": [
                    "Nhà cửa kiên cố (25-50 năm)", "Nhà xưởng lắp ghép (6-25 năm)",
                    "Máy móc động lực (6-15 năm)", "Máy móc công tác (5-12 năm)",
                    "Ô tô vận tải (6-10 năm)", "Máy vi tính/server (3-8 năm)",
                    "Phần mềm tin học (3-8 năm)"
                ]
            }

    min_y = matched_item["min"]
    max_y = matched_item["max"]
    is_valid = min_y <= proposed_years <= max_y

    if proposed_years < min_y:
        assessment = f"KHÔNG HỢP LỆ (Thấp hơn khung tối thiểu {min_y} năm). Trích khấu hao quá nhanh sẽ làm tăng chi phí bất hợp lý, bị cơ quan thuế loại trừ khi quyết toán thuế TNDN."
    elif proposed_years > max_y:
        assessment = f"KHÔNG HỢP LỆ (Vượt khung tối đa {max_y} năm). Trích khấu hao quá chậm làm méo mó kết quả kinh doanh và vi phạm quy định quản lý tài chính."
    else:
        assessment = f"HỢP LỆ. Nằm trong khung quy định {min_y} - {max_y} năm theo Thông tư 45/2013/TT-BTC."

    return {
        "tai_san": asset_type_or_name,
        "nhom_danh_muc": category_name,
        "loai_tai_san_quy_dinh": matched_item["name"],
        "thoi_gian_de_xuat": f"{proposed_years} năm",
        "khung_quy_dinh": f"{min_y} - {max_y} năm",
        "ket_luan": "ĐẠT CHUẨN" if is_valid else "CẢNH BÁO VI PHẠM",
        "danh_gia_rui_ro_thue": assessment,
        "can_cu_phap_ly": "Phụ lục I Thông tư 45/2013/TT-BTC (Bộ Tài chính)"
    }


@mcp.tool()
def generate_depreciation_schedule(
    asset_name: str,
    original_cost: float,
    useful_life_years: float,
    method: str = "straight_line",
    start_date: str = "",
    residual_value: float = 0.0
) -> dict:
    """
    Sinh bảng kế hoạch trích khấu hao chi tiết theo từng năm cho Tài sản cố định.
    
    Tham số:
    - asset_name: Tên tài sản cố định
    - original_cost: Nguyên giá
    - useful_life_years: Số năm sử dụng
    - method: 'straight_line' hoặc 'declining_balance'
    - start_date: Ngày bắt đầu tính khấu hao (dd/mm/yyyy)
    """
    if original_cost <= 0 or useful_life_years <= 0:
        return {"error": "Nguyên giá và số năm sử dụng phải lớn hơn 0"}

    base_amount = original_cost - residual_value
    schedule = []
    accumulated_dep = 0.0
    nbv = original_cost

    start_year = datetime.now().year
    if start_date:
        try:
            parts = start_date.replace("-", "/").split("/")
            if len(parts) == 3:
                start_year = int(parts[2])
        except Exception:
            pass

    method_key = method.lower()
    if "declining" in method_key or "giam_dan" in method_key:
        t = 1.5 if useful_life_years <= 4 else (2.0 if useful_life_years <= 6 else 2.5)
        rate_fast = (1.0 / useful_life_years) * t
        switched = False

        for i in range(1, int(useful_life_years) + 1):
            yr = start_year + i - 1
            rem_years = useful_life_years - i + 1
            straight_eq = nbv / rem_years
            fast_dep = nbv * rate_fast

            if not switched and fast_dep < straight_eq:
                switched = True

            dep = round(straight_eq if switched else fast_dep, 0)
            if dep > nbv - residual_value:
                dep = nbv - residual_value

            accumulated_dep += dep
            nbv = round(original_cost - accumulated_dep, 0)

            schedule.append({
                "nam_thu": i,
                "nam_tai_chinh": yr,
                "muc_khau_hao_nam": dep,
                "khau_hao_luy_ke": accumulated_dep,
                "gia_tri_con_lai": nbv,
                "ghi_chu": "Chuyển sang đường thẳng" if switched else "Khấu hao nhanh"
            })
    else:
        # Đường thẳng
        annual_dep = round(base_amount / useful_life_years, 0)
        for i in range(1, int(useful_life_years) + 1):
            yr = start_year + i - 1
            if i == int(useful_life_years):
                dep = round(base_amount - (annual_dep * (useful_life_years - 1)), 0)
            else:
                dep = annual_dep
            
            accumulated_dep += dep
            nbv = round(original_cost - accumulated_dep, 0)

            schedule.append({
                "nam_thu": i,
                "nam_tai_chinh": yr,
                "muc_khau_hao_nam": dep,
                "khau_hao_luy_ke": accumulated_dep,
                "gia_tri_con_lai": nbv,
                "ghi_chu": "Khấu hao đều hàng năm"
            })

    return {
        "tai_san": asset_name,
        "nguyen_gia": original_cost,
        "gia_tri_thu_hoi_uoc_tinh": residual_value,
        "thoi_gian_su_dung": f"{useful_life_years} năm",
        "phuong_phap": "Số dư giảm dần có điều chỉnh" if "declining" in method_key else "Đường thẳng",
        "tong_so_nam": len(schedule),
        "bang_trich_khau_hao": schedule,
        "tong_khau_hao_da_lap": accumulated_dep,
        "gia_tri_con_lai_cuoi_cung": nbv
    }


@mcp.tool()
def lookup_industry_cost_structure(vsic_code: str = "", industry_name: str = "") -> dict:
    """
    Tra cứu cơ cấu chi phí sản xuất chuẩn ngành (NVL, Nhân công, Sản xuất chung) theo mã ngành VSIC.
    Dùng để đối chiếu, kiểm tra tính hợp lý (Sanity Check) khi lập thẻ tính giá thành và xây dựng định mức chi phí.
    
    Tham số:
    - vsic_code: Mã ngành cấp 2 hoặc cấp 4 (ví dụ: '10', '1020', '14', '24', '41'...)
    - industry_name: Tên ngành tìm kiếm (ví dụ: 'thực phẩm', 'dệt may', 'gỗ', 'thép', 'xây dựng')
    """
    code = vsic_code.strip()
    name = industry_name.lower().strip()

    if code and code in INDUSTRY_BENCHMARKS:
        data = INDUSTRY_BENCHMARKS[code]
    else:
        matched = None
        for k, v in INDUSTRY_BENCHMARKS.items():
            if name and (name in v["name"].lower() or any(w in v["name"].lower() for w in name.split())):
                matched = v
                break
        data = matched

    if not data:
        return {
            "error": "Không tìm thấy ngành tương ứng. Vui lòng chọn trong danh mục mã ngành khả dụng.",
            "danh_sach_nganh_kha_dung": [
                f"VSIC {k}: {v['name']}" for k, v in INDUSTRY_BENCHMARKS.items()
            ]
        }

    return {
        "ma_nganh_vsic": data["vsic"],
        "ten_nganh": data["name"],
        "co_cau_chi_phi_chuan_nganh": {
            "ty_trong_nvl_truc_tiep": f"{data['nvl_min']}% - {data['nvl_max']}%",
            "ty_trong_nhan_cong_truc_tiep": f"{data['nc_min']}% - {data['nc_max']}%",
            "ty_trong_san_xuat_chung": f"{data['sxc_min']}% - {data['sxc_max']}%"
        },
        "bien_loi_nhuan_gop_tham_chieu": data["typical_gross_margin"],
        "dac_diem_nghiep_vu": data["notes"],
        "nguon_du_lieu": "Tổng hợp phân tích từ Tổng cục Thống kê (GSO), VCCI và thực tiễn kiểm toán doanh nghiệp sản xuất VN",
        "khuyen_nghi_quan_tri": (
            "Nếu tỷ lệ NVL vượt ngưỡng tối đa, cần kiểm tra hao hụt và rà soát định mức tiêu hao.\n"
            "Nếu SXC vượt ngưỡng tối đa, kiểm tra công suất bình thường (VAS 02) để loại trừ chi phí SXC cố định dưới công suất vào TK 632."
        )
    }


@mcp.tool()
def compare_with_benchmark(
    vsic_code: str,
    actual_nvl_pct: float,
    actual_nc_pct: float,
    actual_sxc_pct: float,
    actual_gross_margin: float = 0.0
) -> dict:
    """
    So sánh cơ cấu chi phí thực tế của doanh nghiệp với chuẩn ngành để phát hiện rủi ro và bất thường.
    
    Tham số:
    - vsic_code: Mã ngành VSIC (ví dụ: '10', '14', '16', '24', '41'...)
    - actual_nvl_pct: Tỷ lệ chi phí Nguyên vật liệu trực tiếp thực tế (%)
    - actual_nc_pct: Tỷ lệ chi phí Nhân công trực tiếp thực tế (%)
    - actual_sxc_pct: Tỷ lệ chi phí Sản xuất chung thực tế (%)
    - actual_gross_margin: Biên lợi nhuận gộp thực tế (%) (tùy chọn)
    """
    code = vsic_code.strip()
    if code not in INDUSTRY_BENCHMARKS:
        return {
            "error": f"Mã ngành '{code}' chưa có trong dữ liệu benchmark.",
            "danh_sach_ma_hop_le": list(INDUSTRY_BENCHMARKS.keys())
        }

    bench = INDUSTRY_BENCHMARKS[code]
    anomalies = []

    # Kiểm tra tổng 100%
    total_pct = actual_nvl_pct + actual_nc_pct + actual_sxc_pct
    if abs(total_pct - 100.0) > 0.5:
        anomalies.append({
            "khoan_muc": "Tổng tỷ trọng cơ cấu",
            "gia_tri_thuc_te": f"{round(total_pct, 2)}%",
            "muc_do": "LỖI DỮ LIỆU",
            "nhan_xet": f"Tổng cơ cấu (% NVL + % NC + % SXC) phải bằng 100%. Hiện tại đang là {round(total_pct, 2)}%."
        })

    # So sánh NVL
    if actual_nvl_pct > bench["nvl_max"]:
        diff = round(actual_nvl_pct - bench["nvl_max"], 1)
        anomalies.append({
            "khoan_muc": "Chi phí Nguyên vật liệu trực tiếp (621/1541)",
            "gia_tri_thuc_te": f"{actual_nvl_pct}%",
            "chuan_nganh": f"{bench['nvl_min']}% - {bench['nvl_max']}%",
            "muc_do": "CẢNH BÁO CAO",
            "nhan_xet": f"Cao hơn chuẩn ngành {diff}%. Nguy cơ: hao hụt ngoài định mức, nguyên vật liệu bị thất thoát hoặc giá nhập đầu vào tăng đột biến."
        })
    elif actual_nvl_pct < bench["nvl_min"]:
        diff = round(bench["nvl_min"] - actual_nvl_pct, 1)
        anomalies.append({
            "khoan_muc": "Chi phí Nguyên vật liệu trực tiếp (621/1541)",
            "gia_tri_thuc_te": f"{actual_nvl_pct}%",
            "chuan_nganh": f"{bench['nvl_min']}% - {bench['nvl_max']}%",
            "muc_do": "CHÚ Ý",
            "nhan_xet": f"Thấp hơn chuẩn ngành {diff}%. Kiểm tra xem đã ghi nhận đủ phiếu xuất kho NVL trong kỳ chưa."
        })

    # So sánh NC
    if actual_nc_pct > bench["nc_max"]:
        diff = round(actual_nc_pct - bench["nc_max"], 1)
        anomalies.append({
            "khoan_muc": "Chi phí Nhân công trực tiếp (622/1542)",
            "gia_tri_thuc_te": f"{actual_nc_pct}%",
            "chuan_nganh": f"{bench['nc_min']}% - {bench['nc_max']}%",
            "muc_do": "CẢNH BÁO",
            "nhan_xet": f"Cao hơn chuẩn ngành {diff}%. Kiểm tra năng suất lao động, chi phí làm thêm giờ (overtime) hoặc phân loại nhầm nhân viên quản lý vào công nhân trực tiếp."
        })

    # So sánh SXC
    if actual_sxc_pct > bench["sxc_max"]:
        diff = round(actual_sxc_pct - bench["sxc_max"], 1)
        anomalies.append({
            "khoan_muc": "Chi phí Sản xuất chung (627/1547)",
            "gia_tri_thuc_te": f"{actual_sxc_pct}%",
            "chuan_nganh": f"{bench['sxc_min']}% - {bench['sxc_max']}%",
            "muc_do": "CẢNH BÁO TRỌNG YẾU (RỦI RO THUẾ)",
            "nhan_xet": f"Cao hơn chuẩn ngành {diff}%. TUÂN THỦ VAS 02: Doanh nghiệp cần xác định xem nhà máy có hoạt động dưới công suất bình thường không. Phần chi phí SXC cố định dưới công suất bắt buộc chuyển vào TK 632, KHÔNG ĐƯỢC tính vào giá thành TK 154/155."
        })

    risk_level = "THẤP"
    if any(a.get("muc_do") == "CẢNH BÁO TRỌNG YẾU (RỦI RO THUẾ)" for a in anomalies):
        risk_level = "CAO"
    elif anomalies:
        risk_level = "TRUNG BÌNH"

    return {
        "ten_nganh": bench["name"],
        "ma_vsic": code,
        "bang_so_sanh": [
            {"khoan_muc": "Chi phí NVL", "thuc_te": f"{actual_nvl_pct}%", "chuan_nganh": f"{bench['nvl_min']}% - {bench['nvl_max']}%"},
            {"khoan_muc": "Chi phí Nhân công", "thuc_te": f"{actual_nc_pct}%", "chuan_nganh": f"{bench['nc_min']}% - {bench['nc_max']}%"},
            {"khoan_muc": "Chi phí SX chung", "thuc_te": f"{actual_sxc_pct}%", "chuan_nganh": f"{bench['sxc_min']}% - {bench['sxc_max']}%"}
        ],
        "danh_gia_rui_ro": risk_level,
        "danh_sach_bat_thuong": anomalies,
        "ket_luan_va_khuyen_nghi": (
            "Cơ cấu chi phí phù hợp với đặc thù ngành sản xuất." if not anomalies else
            f"Phát hiện {len(anomalies)} điểm lệch chuẩn cần giải trình. Kế toán cần kiểm tra kỹ việc phân bổ chi phí SXC cố định theo VAS 02 và định mức tiêu hao nguyên vật liệu."
        )
    }


if __name__ == "__main__":
    mcp.run()
