"""
Bank API MCP Server
Kết nối API ngân hàng trực tiếp để đối soát sao kê tự động,
tra cứu số dư và tải lịch sử giao dịch.

Hỗ trợ:
1. Tra cứu giao dịch ngân hàng theo khoảng ngày.
2. Tra cứu số dư tài khoản ngân hàng.
3. Tải sao kê ngân hàng theo tháng.
4. Đối soát tự động giao dịch ngân hàng với sổ kế toán.

Lưu ý bảo mật:
- API key và thông tin xác thực được đọc từ biến môi trường hoặc file .env
- TUYỆT ĐỐI không log hoặc cache thông tin xác thực
- Dữ liệu giao dịch được cache cục bộ trong data/cache/bank/
"""

import os
import json
from datetime import datetime, date, timedelta
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("bank-api")

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cache", "bank")

# Cấu hình API ngân hàng — đọc từ biến môi trường
# Người dùng cần thiết lập trong .env hoặc system environment
BANK_CONFIGS = {
    "VCB": {
        "name": "Vietcombank",
        "api_base": os.environ.get("VCB_API_BASE", ""),
        "api_key": os.environ.get("VCB_API_KEY", ""),
        "account_number": os.environ.get("VCB_ACCOUNT_NUMBER", ""),
    },
    "BIDV": {
        "name": "BIDV",
        "api_base": os.environ.get("BIDV_API_BASE", ""),
        "api_key": os.environ.get("BIDV_API_KEY", ""),
        "account_number": os.environ.get("BIDV_ACCOUNT_NUMBER", ""),
    },
    "TCB": {
        "name": "Techcombank",
        "api_base": os.environ.get("TCB_API_BASE", ""),
        "api_key": os.environ.get("TCB_API_KEY", ""),
        "account_number": os.environ.get("TCB_ACCOUNT_NUMBER", ""),
    },
    "MBB": {
        "name": "MB Bank",
        "api_base": os.environ.get("MBB_API_BASE", ""),
        "api_key": os.environ.get("MBB_API_KEY", ""),
        "account_number": os.environ.get("MBB_ACCOUNT_NUMBER", ""),
    },
}


def _ensure_cache_dir():
    """Tạo thư mục cache nếu chưa tồn tại."""
    os.makedirs(CACHE_DIR, exist_ok=True)


def _get_bank_config(bank_code: str) -> dict:
    """Lấy cấu hình API cho ngân hàng chỉ định."""
    bank_code = bank_code.upper().strip()
    if bank_code not in BANK_CONFIGS:
        return {"error": f"Ngân hàng '{bank_code}' chưa được hỗ trợ. Các ngân hàng khả dụng: {', '.join(BANK_CONFIGS.keys())}"}
    config = BANK_CONFIGS[bank_code]
    if not config.get("api_base") or not config.get("api_key"):
        return {
            "error": f"Chưa cấu hình API cho {config['name']}. "
                     f"Vui lòng thiết lập biến môi trường {bank_code}_API_BASE, {bank_code}_API_KEY, {bank_code}_ACCOUNT_NUMBER trong file .env"
        }
    return config


def _make_bank_request(url: str, headers: dict, params: dict = None) -> dict:
    """Gửi request đến API ngân hàng với xử lý lỗi."""
    try:
        import requests
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except ImportError:
        return {"error": "Thư viện 'requests' chưa được cài đặt. Chạy: pip install requests"}
    except Exception as e:
        return {"error": f"Lỗi kết nối API ngân hàng: {str(e)}"}


def _cache_transactions(bank_code: str, period: str, data: list):
    """Lưu cache giao dịch theo kỳ."""
    _ensure_cache_dir()
    cache_file = os.path.join(CACHE_DIR, f"{bank_code}_{period}.json")
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump({
            "bank": bank_code,
            "period": period,
            "cached_at": datetime.now().isoformat(),
            "transactions": data
        }, f, ensure_ascii=False, indent=2)


def _load_cached_transactions(bank_code: str, period: str) -> list:
    """Đọc cache giao dịch nếu có."""
    cache_file = os.path.join(CACHE_DIR, f"{bank_code}_{period}.json")
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            cached = json.load(f)
            return cached.get("transactions", [])
    return []


@mcp.tool()
def get_bank_transactions(
    bank_code: str = "VCB",
    from_date: str = "",
    to_date: str = "",
    account_number: str = ""
) -> dict:
    """
    Lấy danh sách giao dịch ngân hàng theo khoảng ngày.
    
    Tham số:
    - bank_code: Mã ngân hàng (VCB, BIDV, TCB, MBB)
    - from_date: Ngày bắt đầu (dd/mm/yyyy). Mặc định: đầu tháng hiện tại
    - to_date: Ngày kết thúc (dd/mm/yyyy). Mặc định: hôm nay
    - account_number: Số tài khoản (mặc định lấy từ cấu hình .env)
    
    Trả về: danh sách giao dịch gồm ngày, mô tả, số tiền ghi nợ/có, số dư sau giao dịch.
    
    ⚠️ YÊU CẦU: Cấu hình biến môi trường API ngân hàng trong .env trước khi sử dụng.
    """
    config = _get_bank_config(bank_code)
    if "error" in config:
        return config
    
    # Mặc định: đầu tháng đến hôm nay
    today = date.today()
    if not from_date:
        from_date = today.replace(day=1).strftime("%d/%m/%Y")
    if not to_date:
        to_date = today.strftime("%d/%m/%Y")
    
    acct = account_number or config.get("account_number", "")
    if not acct:
        return {"error": f"Chưa cấu hình số tài khoản cho {config['name']}. Thiết lập {bank_code}_ACCOUNT_NUMBER trong .env"}
    
    # Thử đọc cache trước
    period_key = f"{from_date.replace('/', '')}_{to_date.replace('/', '')}"
    cached = _load_cached_transactions(bank_code, period_key)
    if cached:
        return {
            "bank": config["name"],
            "account": acct[:4] + "****" + acct[-4:] if len(acct) > 8 else "****",
            "from_date": from_date,
            "to_date": to_date,
            "transactions": cached,
            "total_transactions": len(cached),
            "source": "Cache cục bộ",
            "note": "Dữ liệu từ cache. Gọi lại với force_refresh=True để cập nhật từ ngân hàng."
        }

    # Gọi API ngân hàng
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    params = {
        "accountNumber": acct,
        "fromDate": from_date,
        "toDate": to_date
    }
    
    result = _make_bank_request(f"{config['api_base']}/transactions", headers, params)
    if "error" in result:
        return {
            "error": result["error"],
            "fallback_suggestion": (
                f"Không thể kết nối API {config['name']}. Giải pháp thay thế:\n"
                f"1. Tải sao kê Excel thủ công từ Internet Banking\n"
                f"2. Đặt file vào: f:/Accountant/data/ngan_hang/sao_ke/\n"
                f"3. Sử dụng skill 'doi-soat-ngan-hang' để đối soát từ file Excel"
            )
        }
    
    transactions = result.get("data", {}).get("transactions", [])
    # Cache kết quả
    _cache_transactions(bank_code, period_key, transactions)
    
    return {
        "bank": config["name"],
        "account": acct[:4] + "****" + acct[-4:] if len(acct) > 8 else "****",
        "from_date": from_date,
        "to_date": to_date,
        "transactions": transactions,
        "total_transactions": len(transactions),
        "source": f"API {config['name']} trực tiếp"
    }


@mcp.tool()
def get_account_balance(
    bank_code: str = "VCB",
    account_number: str = ""
) -> dict:
    """
    Tra cứu số dư tài khoản ngân hàng tại thời điểm hiện tại.
    
    Tham số:
    - bank_code: Mã ngân hàng (VCB, BIDV, TCB, MBB)
    - account_number: Số tài khoản (mặc định lấy từ cấu hình .env)
    
    Trả về: Số dư khả dụng, số dư hiện tại, và thông tin tài khoản.
    
    ⚠️ YÊU CẦU: Cấu hình biến môi trường API ngân hàng trong .env trước khi sử dụng.
    """
    config = _get_bank_config(bank_code)
    if "error" in config:
        return config
    
    acct = account_number or config.get("account_number", "")
    if not acct:
        return {"error": f"Chưa cấu hình số tài khoản cho {config['name']}"}
    
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }
    
    result = _make_bank_request(f"{config['api_base']}/balance", headers, {"accountNumber": acct})
    if "error" in result:
        return {
            "error": result["error"],
            "fallback_suggestion": "Tra cứu số dư trực tiếp trên Internet Banking hoặc ứng dụng ngân hàng."
        }
    
    balance_data = result.get("data", {})
    return {
        "bank": config["name"],
        "account": acct[:4] + "****" + acct[-4:] if len(acct) > 8 else "****",
        "available_balance": balance_data.get("availableBalance", 0),
        "current_balance": balance_data.get("currentBalance", 0),
        "currency": balance_data.get("currency", "VND"),
        "timestamp": datetime.now().isoformat(),
        "note": "Số dư tại thời điểm truy vấn, có thể thay đổi theo giao dịch realtime."
    }


@mcp.tool()
def download_bank_statement(
    bank_code: str = "VCB",
    month: int = 0,
    year: int = 0,
    output_format: str = "json"
) -> dict:
    """
    Tải sao kê ngân hàng theo tháng và lưu vào thư mục dữ liệu.
    
    Tham số:
    - bank_code: Mã ngân hàng (VCB, BIDV, TCB, MBB)
    - month: Tháng cần tải (1-12). Mặc định: tháng hiện tại
    - year: Năm. Mặc định: năm hiện tại
    - output_format: Định dạng xuất (json, csv). Mặc định: json
    
    Trả về: Đường dẫn file sao kê đã lưu và tóm tắt giao dịch.
    
    ⚠️ YÊU CẦU: Cấu hình biến môi trường API ngân hàng trong .env trước khi sử dụng.
    """
    config = _get_bank_config(bank_code)
    if "error" in config:
        return config
    
    today = date.today()
    if month == 0:
        month = today.month
    if year == 0:
        year = today.year
    
    from_date = f"01/{month:02d}/{year}"
    if month == 12:
        last_day = 31
    else:
        last_day = (date(year, month + 1, 1) - timedelta(days=1)).day
    to_date = f"{last_day:02d}/{month:02d}/{year}"
    
    # Gọi API lấy giao dịch
    transactions_result = get_bank_transactions(bank_code, from_date, to_date)
    if "error" in transactions_result:
        return transactions_result
    
    transactions = transactions_result.get("transactions", [])
    
    # Lưu file sao kê
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "ngan_hang", "sao_ke", f"{year}-{month:02d}"
    )
    os.makedirs(output_dir, exist_ok=True)
    
    if output_format == "csv":
        output_file = os.path.join(output_dir, f"sao_ke_{bank_code}_{year}{month:02d}.csv")
        try:
            import pandas as pd
            df = pd.DataFrame(transactions)
            df.to_csv(output_file, index=False, encoding="utf-8-sig")
        except ImportError:
            return {"error": "Thư viện 'pandas' chưa được cài đặt để xuất CSV."}
    else:
        output_file = os.path.join(output_dir, f"sao_ke_{bank_code}_{year}{month:02d}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "bank": config["name"],
                "period": f"{month:02d}/{year}",
                "downloaded_at": datetime.now().isoformat(),
                "total_transactions": len(transactions),
                "transactions": transactions
            }, f, ensure_ascii=False, indent=2)
    
    # Tính tóm tắt
    total_debit = sum(t.get("debit", 0) for t in transactions if isinstance(t.get("debit"), (int, float)))
    total_credit = sum(t.get("credit", 0) for t in transactions if isinstance(t.get("credit"), (int, float)))
    
    return {
        "status": "success",
        "output_file": output_file,
        "bank": config["name"],
        "period": f"{month:02d}/{year}",
        "total_transactions": len(transactions),
        "summary": {
            "tong_phat_sinh_no": total_debit,
            "tong_phat_sinh_co": total_credit,
            "chenh_lech": total_credit - total_debit
        },
        "note": f"Sao kê đã được lưu tại: {output_file}"
    }


DEFAULT_LEDGER_DB = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "database", "ketoan.db"
)


@mcp.tool()
def reconcile_bank_with_ledger(
    bank_code: str = "VCB",
    month: int = 0,
    year: int = 0,
    ledger_db_path: str = "",
    account_code: str = "1121"
) -> dict:
    """
    Đối soát tự động giao dịch ngân hàng với sổ kế toán TK 112 (Tiền gửi không kỳ hạn).
    
    Tham số:
    - bank_code: Mã ngân hàng (VCB, BIDV, TCB, MBB)
    - month: Tháng đối soát (1-12). Mặc định: tháng hiện tại
    - year: Năm. Mặc định: năm hiện tại
    - ledger_db_path: Đường dẫn file SQLite sổ kế toán (để trống để tự động lấy data/database/ketoan.db của dự án)
    - account_code: Tài khoản kế toán đối soát (mặc định 1121 - Tiền VND gửi không kỳ hạn)
    
    Trả về: Kết quả đối soát gồm giao dịch khớp, giao dịch chênh lệch và khuyến nghị.
    """
    db_file = ledger_db_path.strip() if ledger_db_path else DEFAULT_LEDGER_DB
    today = date.today()
    if month == 0:
        month = today.month
    if year == 0:
        year = today.year
    
    # Bước 1: Lấy giao dịch ngân hàng
    from_date = f"01/{month:02d}/{year}"
    if month == 12:
        last_day = 31
    else:
        last_day = (date(year, month + 1, 1) - timedelta(days=1)).day
    to_date = f"{last_day:02d}/{month:02d}/{year}"
    
    bank_result = get_bank_transactions(bank_code, from_date, to_date)
    bank_txns = bank_result.get("transactions", [])
    
    # Bước 2: Lấy bút toán kế toán từ sổ cái
    ledger_txns = []
    if os.path.exists(db_file):
        try:
            import sqlite3
            conn = sqlite3.connect(db_file)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Thử bảng nhat_ky_chung trước (chuẩn lưu trữ của dự án)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='nhat_ky_chung'")
            has_nkc = cursor.fetchone()
            if has_nkc:
                cursor.execute("""
                    SELECT ngay_ghi_so as transaction_date, dien_giai as description, so_tien as amount, tk_no, tk_co
                    FROM nhat_ky_chung
                    WHERE (tk_no LIKE ? OR tk_co LIKE ?)
                    AND ngay_ghi_so BETWEEN ? AND ?
                    ORDER BY ngay_ghi_so
                """, (
                    f"{account_code}%", f"{account_code}%",
                    f"{year}-{month:02d}-01", f"{year}-{month:02d}-{last_day:02d}"
                ))
                ledger_txns = [dict(row) for row in cursor.fetchall()]
            else:
                cursor.execute("""
                    SELECT * FROM journal_entries
                    WHERE (debit_account LIKE ? OR credit_account LIKE ?)
                    AND transaction_date BETWEEN ? AND ?
                    ORDER BY transaction_date
                """, (
                    f"{account_code}%", f"{account_code}%",
                    f"{year}-{month:02d}-01", f"{year}-{month:02d}-{last_day:02d}"
                ))
                ledger_txns = [dict(row) for row in cursor.fetchall()]
            conn.close()
        except Exception as e:
            return {
                "warning": f"Không thể đọc sổ kế toán: {str(e)}",
                "fallback": "Sử dụng skill 'doi-soat-ngan-hang' để đối soát thủ công từ file Excel."
            }
    else:
        return {
            "error": f"Không tìm thấy file sổ kế toán: {db_file}",
            "fallback": "Sử dụng skill 'doi-soat-ngan-hang' để đối soát thủ công từ file Excel."
        }
    
    # Bước 3: Đối soát
    matched = []
    bank_only = []  # Có trên sao kê, chưa ghi sổ
    ledger_only = []  # Đã ghi sổ, chưa có trên sao kê
    
    matched_bank_ids = set()
    matched_ledger_ids = set()
    
    for b_txn in bank_txns:
        b_amount = b_txn.get("credit", 0) or b_txn.get("debit", 0) or 0
        b_date = b_txn.get("date", "")
        found = False
        
        for idx, l_txn in enumerate(ledger_txns):
            if idx in matched_ledger_ids:
                continue
            l_amount = l_txn.get("amount", 0)
            l_date = l_txn.get("transaction_date", "")
            
            # Khớp theo số tiền và ngày giao dịch
            if abs(b_amount - l_amount) < 1 and b_date == l_date:
                matched.append({
                    "bank_txn": b_txn,
                    "ledger_txn": l_txn,
                    "amount": b_amount,
                    "date": b_date
                })
                matched_bank_ids.add(id(b_txn))
                matched_ledger_ids.add(idx)
                found = True
                break
        
        if not found:
            bank_only.append(b_txn)
    
    for idx, l_txn in enumerate(ledger_txns):
        if idx not in matched_ledger_ids:
            ledger_only.append(l_txn)
    
    return {
        "bank": BANK_CONFIGS.get(bank_code.upper(), {}).get("name", bank_code),
        "period": f"{month:02d}/{year}",
        "account_code": account_code,
        "summary": {
            "total_bank_transactions": len(bank_txns),
            "total_ledger_entries": len(ledger_txns),
            "matched": len(matched),
            "bank_only": len(bank_only),
            "ledger_only": len(ledger_only),
            "reconciliation_status": "Cân đối" if not bank_only and not ledger_only else "Có chênh lệch"
        },
        "unreconciled": {
            "bank_only_transactions": bank_only[:20],  # Giới hạn hiển thị
            "ledger_only_entries": ledger_only[:20],
        },
        "recommendations": _generate_reconciliation_recommendations(bank_only, ledger_only),
        "note": (
            "Đối soát dựa trên số tiền và ngày giao dịch. "
            "Các giao dịch chênh lệch cần được kế toán xác minh thủ công. "
            "Xem chi tiết tại skill 'doi-soat-ngan-hang' để xử lý các trường hợp phức tạp."
        )
    }


def _generate_reconciliation_recommendations(bank_only: list, ledger_only: list) -> list:
    """Sinh khuyến nghị xử lý cho các giao dịch chênh lệch."""
    recommendations = []
    
    if bank_only:
        recommendations.append({
            "type": "BANK_NOT_IN_LEDGER",
            "count": len(bank_only),
            "action": "Kiểm tra và bổ sung bút toán kế toán cho các giao dịch có trên sao kê ngân hàng nhưng chưa ghi sổ.",
            "common_causes": [
                "Phí dịch vụ ngân hàng chưa hạch toán",
                "Lãi tiền gửi chưa ghi nhận",
                "Giao dịch thanh toán cuối tháng chưa nhận chứng từ",
                "Khách hàng chuyển tiền chưa thông báo"
            ]
        })
    
    if ledger_only:
        recommendations.append({
            "type": "LEDGER_NOT_IN_BANK",
            "count": len(ledger_only),
            "action": "Kiểm tra lại bút toán kế toán đã ghi nhưng chưa phản ánh trên sao kê ngân hàng.",
            "common_causes": [
                "Séc đã phát hành nhưng chưa thanh toán (Outstanding checks)",
                "Ủy nhiệm chi đã lập nhưng ngân hàng chưa xử lý",
                "Ghi nhầm kỳ kế toán",
                "Bút toán ghi sổ sai tài khoản ngân hàng"
            ]
        })
    
    if not bank_only and not ledger_only:
        recommendations.append({
            "type": "BALANCED",
            "action": "✅ Sổ kế toán và sao kê ngân hàng đã cân đối hoàn toàn. Không cần điều chỉnh."
        })
    
    return recommendations


@mcp.tool()
def list_supported_banks() -> dict:
    """
    Liệt kê các ngân hàng được hỗ trợ và trạng thái cấu hình API.
    
    Trả về: Danh sách ngân hàng, trạng thái kết nối (Đã cấu hình / Chưa cấu hình),
    và hướng dẫn thiết lập cho các ngân hàng chưa cấu hình.
    """
    banks = []
    for code, config in BANK_CONFIGS.items():
        has_api = bool(config.get("api_base")) and bool(config.get("api_key"))
        has_account = bool(config.get("account_number"))
        banks.append({
            "code": code,
            "name": config["name"],
            "api_configured": has_api,
            "account_configured": has_account,
            "status": "✅ Đã cấu hình" if (has_api and has_account) else "⚠️ Chưa cấu hình",
            "env_vars_needed": [
                f"{code}_API_BASE",
                f"{code}_API_KEY",
                f"{code}_ACCOUNT_NUMBER"
            ] if not (has_api and has_account) else []
        })
    
    return {
        "supported_banks": banks,
        "setup_guide": (
            "Để cấu hình API ngân hàng, thêm các biến sau vào file .env:\n"
            "  VCB_API_BASE=https://api.vietcombank.com.vn/v1\n"
            "  VCB_API_KEY=your_api_key_here\n"
            "  VCB_ACCOUNT_NUMBER=0123456789\n\n"
            "Lưu ý: Cần đăng ký Open Banking API từ ngân hàng tương ứng.\n"
            "Nếu chưa có API, sử dụng phương pháp thay thế:\n"
            "  1. Tải sao kê Excel từ Internet Banking\n"
            "  2. Đặt vào thư mục: data/ngan_hang/sao_ke/YYYY-MM/\n"
            "  3. Dùng skill 'doi-soat-ngan-hang' để đối soát"
        ),
        "note": "⚠️ Open Banking API tại Việt Nam hiện đang ở giai đoạn triển khai thí điểm. "
                "Liên hệ bộ phận CNTT của ngân hàng để đăng ký."
    }


if __name__ == "__main__":
    mcp.run()
