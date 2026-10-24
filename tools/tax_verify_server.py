"""
Tax-Verify MCP Server
Chuyên phục vụ công tác xác minh thuế và hóa đơn điện tử Việt Nam:
1. Xác minh hóa đơn điện tử qua Cổng thông tin hóa đơn điện tử (hoadondientu.gdt.gov.vn).
2. Tra cứu hóa đơn theo mã tra cứu in trên hóa đơn.
3. Tra cứu thông tin doanh nghiệp theo Mã số thuế (MST).
4. Đối chiếu thông tin doanh nghiệp trên hóa đơn với cơ sở dữ liệu đăng ký thuế.
5. Kiểm tra chỉ số rủi ro thuế của MST.
6. Tính toán các hạn nộp thuế theo quy định pháp luật.
7. Tính tiền chậm nộp thuế theo Luật Quản lý thuế.
"""

import os
import json
import unicodedata
from datetime import datetime, date, timedelta
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("tax-verify")

# ──────────────────────────── Thư mục cache ────────────────────────────
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cache", "mst")
os.makedirs(CACHE_DIR, exist_ok=True)

# ──────────────────────────── Hằng số ────────────────────────────
_BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
}

_GDT_EINVOICE_URL = "https://hoadondientu.gdt.gov.vn"
_GDT_TRACUU_NNT_URL = "https://tracuunnt.gdt.gov.vn"
_MASOTHUE_API_URL = "https://api.vietqr.io/v2/business"  # API phụ trợ tra cứu MST

# Ngày chuyển giao mốc lãi suất chậm nộp: Luật 108/2025 hiệu lực 01/07/2026
_LUAT_108_EFFECTIVE = date(2026, 7, 1)


# ──────────────────────────── Hàm tiện ích ────────────────────────────

def _normalize_vietnamese(text: str) -> str:
    """
    Chuẩn hóa chuỗi tiếng Việt: bỏ dấu, chuyển thường, loại ký tự đặc biệt.
    Dùng để so sánh fuzzy tên doanh nghiệp, địa chỉ.
    """
    if not text:
        return ""
    # Bỏ dấu tiếng Việt bằng NFD decomposition
    nfkd = unicodedata.normalize("NFD", text)
    stripped = "".join(c for c in nfkd if unicodedata.category(c) != "Mn")
    # Xử lý đ/Đ riêng vì NFD không tách được
    stripped = stripped.replace("đ", "d").replace("Đ", "D")
    # Chuyển thường, gom khoảng trắng
    return " ".join(stripped.lower().split())


def _parse_date_vn(date_str: str) -> date | None:
    """Phân tích chuỗi ngày dạng dd/mm/yyyy hoặc yyyy-mm-dd sang date object."""
    if not date_str:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    return None


def _format_date_vn(d: date) -> str:
    """Định dạng date sang dd/mm/yyyy."""
    return d.strftime("%d/%m/%Y")


def _read_cache(tax_code: str) -> dict | None:
    """Đọc cache MST nếu còn hiệu lực (< 30 ngày)."""
    safe_name = tax_code.replace("-", "_")
    cache_path = os.path.join(CACHE_DIR, f"{safe_name}.json")
    if not os.path.exists(cache_path):
        return None
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            cached = json.load(f)
        cached_time = datetime.fromisoformat(cached.get("_cached_at", ""))
        if (datetime.now() - cached_time).days < 30:
            return cached
    except Exception:
        pass
    return None


def _write_cache(tax_code: str, data: dict):
    """Ghi cache MST ra file JSON."""
    safe_name = tax_code.replace("-", "_")
    cache_path = os.path.join(CACHE_DIR, f"{safe_name}.json")
    try:
        data["_cached_at"] = datetime.now().isoformat()
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _fuzzy_match(a: str, b: str, threshold: float = 0.85) -> tuple[bool, float]:
    """
    So sánh fuzzy hai chuỗi sau khi chuẩn hóa.
    Trả về (is_match, similarity_ratio).
    """
    na = _normalize_vietnamese(a)
    nb = _normalize_vietnamese(b)
    if not na or not nb:
        return False, 0.0
    if na == nb:
        return True, 1.0
    # Tính Jaccard similarity trên từ
    set_a = set(na.split())
    set_b = set(nb.split())
    if not set_a or not set_b:
        return False, 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    ratio = len(intersection) / len(union)
    return ratio >= threshold, round(ratio, 4)


def _scrape_masothue(tax_code: str) -> dict | None:
    """
    Tra cứu MST từ masothue.com (HTML scraping) — Nguồn Cấp 2.
    Trả về dict thông tin doanh nghiệp hoặc None nếu lỗi.
    """
    import requests
    from bs4 import BeautifulSoup

    url = f"https://masothue.com/{tax_code}"
    try:
        resp = requests.get(url, headers=_BROWSER_HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception:
        return None

    try:
        soup = BeautifulSoup(resp.text, "html.parser")
        # Tên công ty
        title_tag = soup.find("h1", class_="tax-title")
        company_name = title_tag.get_text(strip=True) if title_tag else ""
        # Bảng thông tin
        info = {}
        table = soup.find("table", class_="table-taxinfo") or soup.find("table")
        if table:
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True).rstrip(":")
                    value = cells[1].get_text(strip=True)
                    info[label] = value

        # Ánh xạ tên trường
        result = {
            "company_name": company_name,
            "tax_code": tax_code,
            "address": info.get("Địa chỉ", info.get("Địa chỉ trụ sở", "")),
            "representative": info.get("Người đại diện", info.get("Giám đốc", "")),
            "registration_date": info.get("Ngày hoạt động", info.get("Ngày cấp", "")),
            "status": info.get("Tình trạng", "Không xác định"),
            "managing_tax_authority": info.get("Quản lý bởi", info.get("Cơ quan thuế quản lý", "")),
            "source_url": url,
        }
        if result["company_name"]:
            return result
    except Exception:
        pass
    return None


def _scrape_tracuunnt(tax_code: str) -> dict | None:
    """
    Tra cứu MST từ tracuunnt.gdt.gov.vn (Nguồn Cấp 1 — Tổng cục Thuế).
    Trả về dict thông tin doanh nghiệp hoặc None nếu lỗi.
    """
    import requests

    # GDT cung cấp API JSON nội bộ
    api_url = f"{_GDT_TRACUU_NNT_URL}/api/tax-code/{tax_code}"
    try:
        resp = requests.get(api_url, headers=_BROWSER_HEADERS, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if data:
                return {
                    "company_name": data.get("name", data.get("tenNnt", "")),
                    "tax_code": tax_code,
                    "address": data.get("address", data.get("diaChi", "")),
                    "representative": data.get("representative", data.get("nguoiDaiDien", "")),
                    "registration_date": data.get("registrationDate", data.get("ngayDkkd", "")),
                    "status": data.get("status", data.get("tinhTrang", "Không xác định")),
                    "managing_tax_authority": data.get("managingAuthority", data.get("coQuanThue", "")),
                    "source_url": f"{_GDT_TRACUU_NNT_URL}/tracuunnt/detail/{tax_code}",
                }
    except Exception:
        pass

    # Fallback: scraping HTML
    from bs4 import BeautifulSoup
    try:
        page_url = f"{_GDT_TRACUU_NNT_URL}/tracuunnt/detail/{tax_code}"
        resp = requests.get(page_url, headers=_BROWSER_HEADERS, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            info = {}
            for row in soup.select("table tr"):
                cells = row.find_all("td")
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True).rstrip(":")
                    value = cells[1].get_text(strip=True)
                    info[label] = value
            name_tag = soup.find("h3") or soup.find("h2")
            company_name = name_tag.get_text(strip=True) if name_tag else info.get("Tên người nộp thuế", "")
            if company_name:
                return {
                    "company_name": company_name,
                    "tax_code": tax_code,
                    "address": info.get("Địa chỉ", ""),
                    "representative": info.get("Người đại diện pháp luật", ""),
                    "registration_date": info.get("Ngày bắt đầu hoạt động", ""),
                    "status": info.get("Trạng thái", "Không xác định"),
                    "managing_tax_authority": info.get("Cơ quan thuế quản lý", ""),
                    "source_url": page_url,
                }
    except Exception:
        pass
    return None


def _query_vietqr_business(tax_code: str) -> dict | None:
    """
    Tra cứu MST qua VietQR public API (Nguồn phụ trợ, miễn phí).
    """
    import requests
    try:
        resp = requests.get(f"{_MASOTHUE_API_URL}/{tax_code}", headers=_BROWSER_HEADERS, timeout=10)
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            if data and data.get("name"):
                return {
                    "company_name": data.get("name", ""),
                    "tax_code": tax_code,
                    "address": data.get("address", ""),
                    "representative": "",
                    "registration_date": "",
                    "status": "Không xác định (nguồn VietQR không cung cấp trạng thái)",
                    "managing_tax_authority": "",
                    "source_url": f"https://api.vietqr.io/v2/business/{tax_code}",
                }
    except Exception:
        pass
    return None


# ──────────────────────────── MCP TOOLS ────────────────────────────

@mcp.tool()
def verify_einvoice(
    seller_tax_code: str,
    invoice_symbol: str,
    invoice_number: str,
    invoice_date: str = ""
) -> dict:
    """
    Xác minh hóa đơn điện tử qua Cổng thông tin hóa đơn điện tử Tổng cục Thuế.
    Truy vấn hoadondientu.gdt.gov.vn để kiểm tra trạng thái hóa đơn:
    Hợp lệ / Đã hủy / Đã thay thế / Đã điều chỉnh / Không tìm thấy.

    Tham số:
      - seller_tax_code: MST người bán (ví dụ: "0101234567")
      - invoice_symbol: Ký hiệu hóa đơn (ví dụ: "1C26TAA")
      - invoice_number: Số hóa đơn (ví dụ: "00000123")
      - invoice_date: Ngày lập hóa đơn dd/mm/yyyy (tùy chọn, tăng độ chính xác tra cứu)

    Trả về dict chứa verification_status, invoice_details và verification_timestamp.
    """
    import requests

    if not seller_tax_code or not invoice_symbol or not invoice_number:
        return {"error": "Thiếu thông tin bắt buộc: MST người bán, ký hiệu và số hóa đơn."}

    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Xây dựng payload tra cứu
    payload = {
        "mst": seller_tax_code.strip(),
        "khhdon": invoice_symbol.strip(),
        "shdon": invoice_number.strip(),
    }
    if invoice_date:
        payload["nlap"] = invoice_date.strip()

    # Thử API JSON của cổng GDT
    api_url = f"{_GDT_EINVOICE_URL}/api/InvoiceAPI/InquiryInvoice"
    try:
        resp = requests.post(
            api_url,
            json=payload,
            headers={**_BROWSER_HEADERS, "Content-Type": "application/json"},
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            status_code = data.get("status", data.get("tthai", ""))
            status_map = {
                "1": "Hợp lệ",
                "2": "Đã hủy",
                "3": "Đã thay thế",
                "4": "Đã điều chỉnh",
                "5": "Đã bị thu hồi",
            }
            verification_status = status_map.get(str(status_code), f"Mã trạng thái: {status_code}")
            return {
                "verification_status": verification_status,
                "invoice_details": {
                    "seller_tax_code": seller_tax_code,
                    "invoice_symbol": invoice_symbol,
                    "invoice_number": invoice_number,
                    "invoice_date": invoice_date or "(không cung cấp)",
                    "seller_name": data.get("nbmst", data.get("tenNban", "")),
                    "total_amount": data.get("tgtttbso", data.get("tongTien", "")),
                },
                "raw_response": data,
                "verification_timestamp": timestamp,
                "source_url": _GDT_EINVOICE_URL,
            }
    except requests.exceptions.Timeout:
        return {
            "error": "Hết thời gian kết nối đến cổng hóa đơn điện tử (timeout 15s).",
            "verification_timestamp": timestamp,
            "suggestion": "Vui lòng thử lại sau hoặc tra cứu trực tiếp tại https://hoadondientu.gdt.gov.vn",
        }
    except requests.exceptions.ConnectionError:
        return {
            "error": "Không thể kết nối đến cổng hóa đơn điện tử Tổng cục Thuế.",
            "verification_timestamp": timestamp,
            "suggestion": "Kiểm tra kết nối mạng hoặc tra cứu trực tiếp tại https://hoadondientu.gdt.gov.vn",
        }
    except Exception as e:
        pass

    # Fallback: thử form submission HTML
    from bs4 import BeautifulSoup
    form_url = f"{_GDT_EINVOICE_URL}/tracuuhoadon"
    try:
        resp = requests.post(
            form_url,
            data=payload,
            headers=_BROWSER_HEADERS,
            timeout=15,
        )
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            result_div = soup.find("div", class_="result") or soup.find("div", id="result")
            if result_div:
                result_text = result_div.get_text(strip=True)
                # Xác định trạng thái từ nội dung phản hồi
                status = "Không xác định"
                for keyword, label in [
                    ("hợp lệ", "Hợp lệ"),
                    ("đã hủy", "Đã hủy"),
                    ("thay thế", "Đã thay thế"),
                    ("điều chỉnh", "Đã điều chỉnh"),
                    ("không tìm thấy", "Không tìm thấy"),
                    ("không tồn tại", "Không tìm thấy"),
                ]:
                    if keyword in result_text.lower():
                        status = label
                        break
                return {
                    "verification_status": status,
                    "invoice_details": {
                        "seller_tax_code": seller_tax_code,
                        "invoice_symbol": invoice_symbol,
                        "invoice_number": invoice_number,
                        "invoice_date": invoice_date or "(không cung cấp)",
                    },
                    "raw_text": result_text[:500],
                    "verification_timestamp": timestamp,
                    "source_url": form_url,
                }
    except Exception as e:
        return {
            "error": f"Lỗi tra cứu hóa đơn điện tử: {str(e)}",
            "verification_timestamp": timestamp,
            "suggestion": "Vui lòng tra cứu trực tiếp tại https://hoadondientu.gdt.gov.vn",
        }

    return {
        "verification_status": "Không thể xác minh",
        "invoice_details": {
            "seller_tax_code": seller_tax_code,
            "invoice_symbol": invoice_symbol,
            "invoice_number": invoice_number,
            "invoice_date": invoice_date or "(không cung cấp)",
        },
        "verification_timestamp": timestamp,
        "suggestion": "Cổng HĐĐT không phản hồi kết quả. Vui lòng thử lại hoặc tra cứu tại https://hoadondientu.gdt.gov.vn",
    }


@mcp.tool()
def lookup_invoice_by_code(lookup_code: str) -> dict:
    """
    Tra cứu hóa đơn điện tử theo mã tra cứu (Mã tra cứu in trên hóa đơn).
    Gửi yêu cầu đến cổng hoadondientu.gdt.gov.vn.

    Tham số:
      - lookup_code: Mã tra cứu hóa đơn (chuỗi ký tự in trên hóa đơn điện tử)

    Trả về dict chứa thông tin hóa đơn: người bán, người mua, tổng tiền, thuế, trạng thái.
    """
    import requests
    from bs4 import BeautifulSoup

    if not lookup_code or not lookup_code.strip():
        return {"error": "Mã tra cứu hóa đơn không được để trống."}

    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    lookup_code = lookup_code.strip()

    # Thử API JSON
    api_url = f"{_GDT_EINVOICE_URL}/api/InvoiceAPI/InquiryByCode"
    try:
        resp = requests.post(
            api_url,
            json={"code": lookup_code},
            headers={**_BROWSER_HEADERS, "Content-Type": "application/json"},
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data and not data.get("error"):
                return {
                    "lookup_code": lookup_code,
                    "invoice_details": {
                        "invoice_symbol": data.get("khhdon", ""),
                        "invoice_number": data.get("shdon", ""),
                        "invoice_date": data.get("nlap", ""),
                        "seller_name": data.get("nbten", data.get("tenNban", "")),
                        "seller_tax_code": data.get("nbmst", data.get("mstNban", "")),
                        "buyer_name": data.get("nmten", data.get("tenNmua", "")),
                        "buyer_tax_code": data.get("nmmst", data.get("mstNmua", "")),
                        "total_before_tax": data.get("tgtcthue", ""),
                        "vat_amount": data.get("tgtthue", ""),
                        "total_amount": data.get("tgtttbso", data.get("tongTien", "")),
                        "status": data.get("tthai", ""),
                    },
                    "raw_response": data,
                    "lookup_timestamp": timestamp,
                    "source_url": _GDT_EINVOICE_URL,
                }
    except Exception:
        pass

    # Fallback: form HTML
    form_url = f"{_GDT_EINVOICE_URL}/tracuumacode"
    try:
        resp = requests.post(
            form_url,
            data={"maTraCuu": lookup_code},
            headers=_BROWSER_HEADERS,
            timeout=15,
        )
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            result_div = soup.find("div", class_="result") or soup.find("div", id="result")
            if result_div:
                return {
                    "lookup_code": lookup_code,
                    "raw_text": result_div.get_text(strip=True)[:1000],
                    "lookup_timestamp": timestamp,
                    "source_url": form_url,
                }
    except Exception as e:
        return {
            "error": f"Lỗi tra cứu hóa đơn theo mã tra cứu: {str(e)}",
            "lookup_timestamp": timestamp,
            "suggestion": "Vui lòng tra cứu trực tiếp tại https://hoadondientu.gdt.gov.vn",
        }

    return {
        "lookup_code": lookup_code,
        "error": "Không nhận được phản hồi từ cổng HĐĐT. Vui lòng thử lại sau.",
        "lookup_timestamp": timestamp,
        "suggestion": "Tra cứu trực tiếp tại https://hoadondientu.gdt.gov.vn",
    }


@mcp.tool()
def lookup_tax_code(tax_code: str) -> dict:
    """
    Tra cứu thông tin doanh nghiệp theo Mã số thuế (MST).
    Ưu tiên nguồn Cấp 1 (tracuunnt.gdt.gov.vn — Tổng cục Thuế),
    fallback sang masothue.com (Cấp 2) và VietQR API.
    Kết quả được cache tại data/cache/mst/ (hiệu lực 30 ngày).

    Tham số:
      - tax_code: Mã số thuế (ví dụ: "0101234567" hoặc "0101234567-001")

    Trả về dict chứa:
      company_name, tax_code, address, representative,
      registration_date, status, managing_tax_authority,
      source_url, lookup_timestamp.
    """
    if not tax_code or not tax_code.strip():
        return {"error": "Mã số thuế không được để trống."}

    tax_code = tax_code.strip()
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Kiểm tra cache trước
    cached = _read_cache(tax_code)
    if cached:
        cached.pop("_cached_at", None)
        cached["lookup_timestamp"] = timestamp
        cached["from_cache"] = True
        return cached

    # Nguồn 1: tracuunnt.gdt.gov.vn (Cấp 1)
    result = _scrape_tracuunnt(tax_code)
    source_tier = "Cấp 1 (Tổng cục Thuế — tracuunnt.gdt.gov.vn)"

    # Nguồn 2: masothue.com (Cấp 2)
    if not result:
        result = _scrape_masothue(tax_code)
        source_tier = "Cấp 2 (masothue.com — tham khảo, cần đối chiếu Cấp 1)"

    # Nguồn 3: VietQR API (phụ trợ)
    if not result:
        result = _query_vietqr_business(tax_code)
        source_tier = "Phụ trợ (VietQR API — thông tin hạn chế)"

    if not result:
        return {
            "error": f"Không tìm thấy thông tin doanh nghiệp cho MST: {tax_code}",
            "lookup_timestamp": timestamp,
            "suggestion": (
                f"Vui lòng tra cứu trực tiếp tại:\n"
                f"  • Cấp 1: {_GDT_TRACUU_NNT_URL}\n"
                f"  • Cấp 2: https://masothue.com/{tax_code}"
            ),
        }

    result["lookup_timestamp"] = timestamp
    result["source_tier"] = source_tier
    result["from_cache"] = False

    # Ghi cache
    _write_cache(tax_code, result.copy())

    return result


@mcp.tool()
def verify_business_info(
    tax_code: str,
    expected_name: str = "",
    expected_address: str = ""
) -> dict:
    """
    Đối chiếu thông tin doanh nghiệp trên hóa đơn với cơ sở dữ liệu đăng ký thuế.
    Tra cứu MST rồi so sánh tên và địa chỉ doanh nghiệp (fuzzy matching, bỏ dấu).

    Tham số:
      - tax_code: Mã số thuế cần xác minh
      - expected_name: Tên doanh nghiệp ghi trên hóa đơn (tùy chọn)
      - expected_address: Địa chỉ doanh nghiệp ghi trên hóa đơn (tùy chọn)

    Trả về dict chứa:
      match_status (Khớp / Không khớp / Cảnh báo),
      mismatched_fields, registered_info, expected_info.
    """
    if not tax_code or not tax_code.strip():
        return {"error": "Mã số thuế không được để trống."}

    # Tra cứu thông tin đăng ký
    registered = lookup_tax_code(tax_code)
    if "error" in registered:
        return {
            "error": f"Không tra cứu được thông tin MST {tax_code}: {registered['error']}",
            "suggestion": "Không thể đối chiếu do không có dữ liệu đăng ký. Vui lòng tra cứu thủ công.",
        }

    mismatched_fields = []
    warnings = []

    # So sánh tên doanh nghiệp
    name_match = True
    name_similarity = 0.0
    if expected_name:
        name_match, name_similarity = _fuzzy_match(expected_name, registered.get("company_name", ""))
        if not name_match:
            if name_similarity >= 0.6:
                warnings.append({
                    "field": "Tên doanh nghiệp",
                    "message": "Tên trên hóa đơn tương tự nhưng không khớp hoàn toàn với đăng ký thuế.",
                    "similarity": name_similarity,
                    "expected": expected_name,
                    "registered": registered.get("company_name", ""),
                })
            else:
                mismatched_fields.append({
                    "field": "Tên doanh nghiệp",
                    "expected": expected_name,
                    "registered": registered.get("company_name", ""),
                    "similarity": name_similarity,
                })

    # So sánh địa chỉ
    address_match = True
    address_similarity = 0.0
    if expected_address:
        address_match, address_similarity = _fuzzy_match(expected_address, registered.get("address", ""), threshold=0.7)
        if not address_match:
            if address_similarity >= 0.5:
                warnings.append({
                    "field": "Địa chỉ",
                    "message": "Địa chỉ trên hóa đơn tương tự nhưng không khớp hoàn toàn.",
                    "similarity": address_similarity,
                    "expected": expected_address,
                    "registered": registered.get("address", ""),
                })
            else:
                mismatched_fields.append({
                    "field": "Địa chỉ",
                    "expected": expected_address,
                    "registered": registered.get("address", ""),
                    "similarity": address_similarity,
                })

    # Xác định trạng thái tổng thể
    if mismatched_fields:
        match_status = "Không khớp"
    elif warnings:
        match_status = "Cảnh báo"
    else:
        match_status = "Khớp"

    return {
        "match_status": match_status,
        "tax_code": tax_code,
        "mismatched_fields": mismatched_fields,
        "warnings": warnings,
        "registered_info": {
            "company_name": registered.get("company_name", ""),
            "address": registered.get("address", ""),
            "status": registered.get("status", ""),
            "representative": registered.get("representative", ""),
            "managing_tax_authority": registered.get("managing_tax_authority", ""),
        },
        "expected_info": {
            "expected_name": expected_name or "(không cung cấp)",
            "expected_address": expected_address or "(không cung cấp)",
        },
        "source_tier": registered.get("source_tier", ""),
        "verification_timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    }


@mcp.tool()
def check_tax_risk_indicators(tax_code: str) -> dict:
    """
    Kiểm tra các chỉ số rủi ro thuế của một Mã số thuế.
    Tra cứu trạng thái MST và đánh giá mức độ rủi ro khi giao dịch.

    Chỉ số rủi ro:
      - Ngừng hoạt động
      - Bỏ địa chỉ kinh doanh
      - Đang bị cưỡng chế thuế
      - MST đã đóng / Đã giải thể

    Tham số:
      - tax_code: Mã số thuế cần kiểm tra

    Trả về dict chứa:
      risk_level (Thấp / Trung bình / Cao),
      indicators (danh sách chỉ số rủi ro phát hiện),
      recommendation (khuyến nghị xử lý).
    """
    if not tax_code or not tax_code.strip():
        return {"error": "Mã số thuế không được để trống."}

    # Tra cứu thông tin
    info = lookup_tax_code(tax_code)
    if "error" in info:
        return {
            "tax_code": tax_code,
            "risk_level": "Không xác định",
            "error": f"Không tra cứu được MST: {info['error']}",
            "recommendation": (
                "Không thể đánh giá rủi ro do không tra cứu được thông tin. "
                "Cần thận trọng và xác minh thủ công trước khi giao dịch."
            ),
        }

    status = info.get("status", "").lower()
    indicators = []

    # Phân tích các chỉ số rủi ro từ trạng thái
    risk_keywords = {
        "ngừng hoạt động": "Doanh nghiệp đã ngừng hoạt động — hóa đơn có thể không hợp lệ.",
        "ngung hoat dong": "Doanh nghiệp đã ngừng hoạt động — hóa đơn có thể không hợp lệ.",
        "bỏ địa chỉ": "Doanh nghiệp bỏ địa chỉ kinh doanh — dấu hiệu rủi ro cao.",
        "bo dia chi": "Doanh nghiệp bỏ địa chỉ kinh doanh — dấu hiệu rủi ro cao.",
        "cưỡng chế": "Doanh nghiệp đang bị cưỡng chế thuế — rủi ro pháp lý nghiêm trọng.",
        "cuong che": "Doanh nghiệp đang bị cưỡng chế thuế — rủi ro pháp lý nghiêm trọng.",
        "đã đóng": "MST đã đóng — doanh nghiệp không còn hoạt động.",
        "da dong": "MST đã đóng — doanh nghiệp không còn hoạt động.",
        "giải thể": "Doanh nghiệp đã giải thể — mọi hóa đơn phát hành đều không hợp lệ.",
        "giai the": "Doanh nghiệp đã giải thể — mọi hóa đơn phát hành đều không hợp lệ.",
        "tạm ngừng": "Doanh nghiệp tạm ngừng kinh doanh — cần xem xét thời điểm giao dịch.",
        "tam ngung": "Doanh nghiệp tạm ngừng kinh doanh — cần xem xét thời điểm giao dịch.",
        "chờ đóng": "MST đang chờ đóng — doanh nghiệp sắp kết thúc hoạt động.",
        "cho dong": "MST đang chờ đóng — doanh nghiệp sắp kết thúc hoạt động.",
    }

    status_normalized = _normalize_vietnamese(status)
    for keyword, description in risk_keywords.items():
        if keyword in status or keyword in status_normalized:
            indicators.append({
                "indicator": keyword.title(),
                "description": description,
            })

    # Xác định mức rủi ro
    if not indicators:
        if "đang hoạt động" in status or "dang hoat dong" in status_normalized:
            risk_level = "Thấp"
            recommendation = "MST đang hoạt động bình thường. Tiếp tục giao dịch với kiểm tra thông thường."
        else:
            risk_level = "Trung bình"
            recommendation = (
                f"Trạng thái MST: \"{info.get('status', 'Không xác định')}\". "
                "Không thuộc các chỉ số rủi ro rõ ràng, nhưng khuyến nghị xác minh thêm với cơ quan thuế quản lý."
            )
    elif len(indicators) >= 2:
        risk_level = "Cao"
        recommendation = (
            "CẢNH BÁO: Phát hiện nhiều chỉ số rủi ro! "
            "Tuyệt đối không sử dụng hóa đơn từ đối tác này để kê khai khấu trừ thuế GTGT. "
            "Cần báo cáo Cơ quan thuế quản lý và rà soát toàn bộ giao dịch liên quan."
        )
    else:
        risk_level = "Cao"
        recommendation = (
            "CẢNH BÁO: Phát hiện chỉ số rủi ro! "
            "Cần thận trọng tối đa: đối chiếu hóa đơn đầu vào, "
            "xác minh tính hợp lệ của giao dịch trước khi kê khai thuế. "
            "Khuyến nghị tham vấn Cơ quan thuế quản lý trực tiếp."
        )

    return {
        "tax_code": tax_code,
        "company_name": info.get("company_name", ""),
        "status": info.get("status", "Không xác định"),
        "risk_level": risk_level,
        "indicators": indicators,
        "recommendation": recommendation,
        "source_tier": info.get("source_tier", ""),
        "check_timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    }


@mcp.tool()
def get_upcoming_deadlines(
    tax_period: str = "",
    company_type: str = "quarterly"
) -> dict:
    """
    Tính toán và trả về các hạn nộp thuế, tờ khai và báo cáo tài chính sắp tới.
    Áp dụng theo Luật Quản lý thuế 108/2025/QH15 (hiệu lực 01/07/2026)
    và Luật 38/2019/QH14 (giai đoạn trước 01/07/2026).

    Tham số:
      - tax_period: Kỳ tính thuế hiện tại (ví dụ: "Q3/2026", "T10/2026").
                    Nếu để trống, tự động xác định theo ngày hiện tại.
      - company_type: Tần suất kê khai GTGT — "monthly" (tháng) hoặc "quarterly" (quý, mặc định).

    Hạn nộp tính toán:
      • Thuế GTGT: Ngày 20 tháng sau (monthly) hoặc ngày cuối tháng đầu quý sau (quarterly)
      • Thuế TNCN: Cùng hạn với GTGT
      • Thuế TNDN tạm tính: Ngày cuối tháng đầu quý sau
      • Quyết toán TNDN: Ngày cuối tháng thứ 3 sau kết thúc năm tài chính
      • Quyết toán TNCN: Ngày cuối tháng thứ 4 sau kết thúc năm (Luật 108/2025)
      • BCTC: Ngày cuối tháng thứ 3 (DN tư nhân) hoặc 4 (DN nhà nước) sau kết thúc năm

    Trả về list các hạn: deadline_name, deadline_date, days_remaining,
    status (Sắp đến hạn / Còn thời gian / Quá hạn), legal_basis.
    """
    today = date.today()
    company_type = company_type.strip().lower()
    if company_type not in ("monthly", "quarterly"):
        company_type = "quarterly"

    # Xác định kỳ tính thuế
    current_year = today.year
    current_month = today.month
    current_quarter = (current_month - 1) // 3 + 1

    tax_period = tax_period.strip() if tax_period else ""
    period_year = current_year
    period_month = current_month
    period_quarter = current_quarter

    if tax_period:
        tp_upper = tax_period.upper().replace(" ", "")
        if tp_upper.startswith("Q") or tp_upper.startswith("QUÝ"):
            # Quý, ví dụ Q3/2026
            parts = tp_upper.replace("QUÝ", "Q").split("/")
            try:
                period_quarter = int(parts[0].replace("Q", ""))
                period_year = int(parts[1]) if len(parts) > 1 else current_year
            except (ValueError, IndexError):
                pass
        elif tp_upper.startswith("T") or tp_upper.startswith("THÁNG"):
            # Tháng, ví dụ T10/2026
            parts = tp_upper.replace("THÁNG", "T").split("/")
            try:
                period_month = int(parts[0].replace("T", ""))
                period_year = int(parts[1]) if len(parts) > 1 else current_year
                period_quarter = (period_month - 1) // 3 + 1
            except (ValueError, IndexError):
                pass

    def _last_day_of_month(year: int, month: int) -> date:
        """Trả về ngày cuối cùng của tháng."""
        if month == 12:
            return date(year, 12, 31)
        return date(year, month + 1, 1) - timedelta(days=1)

    def _deadline_status(deadline_date: date) -> tuple[str, int]:
        """Trả về (trạng thái, số ngày còn lại)."""
        days_remaining = (deadline_date - today).days
        if days_remaining < 0:
            return "Quá hạn", days_remaining
        elif days_remaining <= 7:
            return "⚠️ Sắp đến hạn", days_remaining
        else:
            return "Còn thời gian", days_remaining

    # Căn cứ pháp lý theo thời điểm
    if today >= _LUAT_108_EFFECTIVE:
        luat_ql_thue = "Luật Quản lý thuế số 108/2025/QH15"
    else:
        luat_ql_thue = "Luật Quản lý thuế số 38/2019/QH14 (sửa đổi bởi Luật 56/2024/QH15)"

    deadlines = []

    # ── 1. Thuế GTGT ──
    if company_type == "monthly":
        # Hạn: ngày 20 tháng sau
        deadline_month = period_month + 1
        deadline_year = period_year
        if deadline_month > 12:
            deadline_month = 1
            deadline_year += 1
        gtgt_deadline = date(deadline_year, deadline_month, 20)
        gtgt_name = f"Tờ khai Thuế GTGT tháng {period_month:02d}/{period_year}"
    else:
        # Hạn: ngày cuối tháng đầu quý sau
        next_q_first_month = period_quarter * 3 + 1
        deadline_year = period_year
        if next_q_first_month > 12:
            next_q_first_month -= 12
            deadline_year += 1
        gtgt_deadline = _last_day_of_month(deadline_year, next_q_first_month)
        gtgt_name = f"Tờ khai Thuế GTGT Quý {period_quarter}/{period_year}"

    status, days = _deadline_status(gtgt_deadline)
    deadlines.append({
        "deadline_name": gtgt_name,
        "deadline_date": _format_date_vn(gtgt_deadline),
        "days_remaining": days,
        "status": status,
        "legal_basis": f"{luat_ql_thue}; Luật Thuế GTGT số 48/2024/QH15",
    })

    # ── 2. Thuế TNCN (cùng hạn GTGT) ──
    if company_type == "monthly":
        tncn_name = f"Tờ khai Thuế TNCN tháng {period_month:02d}/{period_year}"
    else:
        tncn_name = f"Tờ khai Thuế TNCN Quý {period_quarter}/{period_year}"

    status, days = _deadline_status(gtgt_deadline)
    deadlines.append({
        "deadline_name": tncn_name,
        "deadline_date": _format_date_vn(gtgt_deadline),
        "days_remaining": days,
        "status": status,
        "legal_basis": f"{luat_ql_thue}; Luật Thuế TNCN số 109/2025/QH15",
    })

    # ── 3. Thuế TNDN tạm tính (quý) ──
    tndn_next_q_first_month = period_quarter * 3 + 1
    tndn_deadline_year = period_year
    if tndn_next_q_first_month > 12:
        tndn_next_q_first_month -= 12
        tndn_deadline_year += 1
    tndn_deadline = _last_day_of_month(tndn_deadline_year, tndn_next_q_first_month)
    status, days = _deadline_status(tndn_deadline)
    deadlines.append({
        "deadline_name": f"Thuế TNDN tạm tính Quý {period_quarter}/{period_year}",
        "deadline_date": _format_date_vn(tndn_deadline),
        "days_remaining": days,
        "status": status,
        "legal_basis": f"{luat_ql_thue}; Luật Thuế TNDN số 67/2025/QH15",
    })

    # ── 4. Quyết toán thuế TNDN (năm) ──
    # Hạn: ngày cuối tháng thứ 3 sau kết thúc năm tài chính (giả định năm tài chính = năm dương lịch)
    qt_tndn_deadline = _last_day_of_month(period_year + 1, 3)
    status, days = _deadline_status(qt_tndn_deadline)
    deadlines.append({
        "deadline_name": f"Quyết toán Thuế TNDN năm {period_year}",
        "deadline_date": _format_date_vn(qt_tndn_deadline),
        "days_remaining": days,
        "status": status,
        "legal_basis": f"{luat_ql_thue}; Luật Thuế TNDN số 67/2025/QH15",
    })

    # ── 5. Quyết toán thuế TNCN (năm) ──
    # Luật 108/2025: ngày cuối tháng thứ 4 sau kết thúc năm tài chính
    qt_tncn_deadline = _last_day_of_month(period_year + 1, 4)
    status, days = _deadline_status(qt_tncn_deadline)
    deadlines.append({
        "deadline_name": f"Quyết toán Thuế TNCN năm {period_year}",
        "deadline_date": _format_date_vn(qt_tncn_deadline),
        "days_remaining": days,
        "status": status,
        "legal_basis": "Luật Quản lý thuế số 108/2025/QH15; Luật Thuế TNCN số 109/2025/QH15",
    })

    # ── 6. Nộp Báo cáo tài chính (BCTC) ──
    # DN tư nhân: 3 tháng; DN nhà nước: 4 tháng (cung cấp cả hai)
    bctc_private = _last_day_of_month(period_year + 1, 3)
    bctc_state = _last_day_of_month(period_year + 1, 4)

    status_p, days_p = _deadline_status(bctc_private)
    deadlines.append({
        "deadline_name": f"Nộp BCTC năm {period_year} (DN tư nhân & FDI)",
        "deadline_date": _format_date_vn(bctc_private),
        "days_remaining": days_p,
        "status": status_p,
        "legal_basis": f"Luật Kế toán số 88/2015/QH13 (sửa đổi bởi Luật 56/2024/QH15); {luat_ql_thue}",
    })

    status_s, days_s = _deadline_status(bctc_state)
    deadlines.append({
        "deadline_name": f"Nộp BCTC năm {period_year} (DN nhà nước)",
        "deadline_date": _format_date_vn(bctc_state),
        "days_remaining": days_s,
        "status": status_s,
        "legal_basis": f"Luật Kế toán số 88/2015/QH13 (sửa đổi bởi Luật 56/2024/QH15); {luat_ql_thue}",
    })

    # Sắp xếp theo ngày hạn
    deadlines.sort(key=lambda d: _parse_date_vn(d["deadline_date"]) or date.max)

    # Đếm cảnh báo
    urgent_count = sum(1 for d in deadlines if "Sắp đến hạn" in d["status"])
    overdue_count = sum(1 for d in deadlines if d["status"] == "Quá hạn")

    return {
        "reference_date": _format_date_vn(today),
        "tax_period": tax_period or f"Q{current_quarter}/{current_year}",
        "company_type": "Kê khai theo tháng" if company_type == "monthly" else "Kê khai theo quý",
        "total_deadlines": len(deadlines),
        "urgent_count": urgent_count,
        "overdue_count": overdue_count,
        "deadlines": deadlines,
    }


@mcp.tool()
def calculate_late_penalty(
    tax_type: str,
    original_amount: float,
    due_date: str,
    payment_date: str = ""
) -> dict:
    """
    Tính tiền chậm nộp thuế theo quy định Luật Quản lý thuế.
    Công thức: Tiền chậm nộp = Số tiền thuế × Tỷ lệ/ngày × Số ngày chậm nộp.

    Tỷ lệ áp dụng:
      - Từ 01/07/2026: 0,03%/ngày (Luật Quản lý thuế số 108/2025/QH15)
      - Trước 01/07/2026: 0,03%/ngày (Luật 38/2019/QH14, Điều 59 Khoản 2)
        Lưu ý: Mức 0,05%/ngày áp dụng cho giai đoạn trước 01/07/2016.

    Tham số:
      - tax_type: Loại thuế — "GTGT", "TNDN" hoặc "TNCN"
      - original_amount: Số tiền thuế phải nộp (VNĐ)
      - due_date: Ngày hạn nộp (dd/mm/yyyy)
      - payment_date: Ngày nộp thực tế (dd/mm/yyyy). Mặc định = ngày hôm nay.

    Trả về dict chứa:
      days_late, daily_rate, total_penalty, total_due,
      legal_basis, calculation_breakdown.
    """
    tax_type = tax_type.strip().upper()
    if tax_type not in ("GTGT", "TNDN", "TNCN"):
        return {"error": f"Loại thuế không hợp lệ: '{tax_type}'. Chấp nhận: GTGT, TNDN, TNCN."}

    if original_amount <= 0:
        return {"error": "Số tiền thuế phải nộp phải lớn hơn 0."}

    due = _parse_date_vn(due_date)
    if not due:
        return {"error": f"Không thể phân tích ngày hạn nộp: '{due_date}'. Định dạng: dd/mm/yyyy."}

    if payment_date:
        pay = _parse_date_vn(payment_date)
        if not pay:
            return {"error": f"Không thể phân tích ngày nộp thực tế: '{payment_date}'. Định dạng: dd/mm/yyyy."}
    else:
        pay = date.today()

    days_late = (pay - due).days
    if days_late <= 0:
        return {
            "tax_type": tax_type,
            "original_amount": original_amount,
            "due_date": _format_date_vn(due),
            "payment_date": _format_date_vn(pay),
            "days_late": 0,
            "total_penalty": 0,
            "total_due": original_amount,
            "message": "Nộp đúng hạn hoặc trước hạn — không phát sinh tiền chậm nộp.",
        }

    # Xác định tỷ lệ và căn cứ pháp lý theo giai đoạn
    # Luật 38/2019 (hiệu lực 01/07/2020): 0.03%/ngày (Điều 59 Khoản 2)
    # Luật 108/2025 (hiệu lực 01/07/2026): 0.03%/ngày
    # Giai đoạn trước 01/07/2016: 0.05%/ngày (Luật 78/2006 sửa đổi)

    _OLD_RATE_CUTOFF = date(2016, 7, 1)  # Mốc chuyển 0.05% → 0.03%

    breakdown = []
    total_penalty = 0.0

    if due < _OLD_RATE_CUTOFF:
        # Giai đoạn 1: từ due đến min(pay, _OLD_RATE_CUTOFF) với 0.05%
        end_old = min(pay, _OLD_RATE_CUTOFF)
        days_old = (end_old - due).days
        if days_old > 0:
            penalty_old = original_amount * 0.0005 * days_old
            total_penalty += penalty_old
            breakdown.append({
                "giai_doan": f"{_format_date_vn(due)} → {_format_date_vn(end_old)}",
                "so_ngay": days_old,
                "ty_le_ngay": "0,05%",
                "tien_cham_nop": round(penalty_old),
                "can_cu": "Luật Quản lý thuế số 78/2006/QH11 (sửa đổi)",
            })
        # Giai đoạn 2: từ _OLD_RATE_CUTOFF đến pay với 0.03%
        if pay > _OLD_RATE_CUTOFF:
            days_new = (pay - _OLD_RATE_CUTOFF).days
            penalty_new = original_amount * 0.0003 * days_new
            total_penalty += penalty_new
            breakdown.append({
                "giai_doan": f"{_format_date_vn(_OLD_RATE_CUTOFF)} → {_format_date_vn(pay)}",
                "so_ngay": days_new,
                "ty_le_ngay": "0,03%",
                "tien_cham_nop": round(penalty_new),
                "can_cu": "Luật Quản lý thuế số 38/2019/QH14, Điều 59 Khoản 2",
            })
    else:
        # Toàn bộ giai đoạn 0.03%
        daily_rate = 0.0003
        penalty = original_amount * daily_rate * days_late
        total_penalty = penalty

        if due >= _LUAT_108_EFFECTIVE:
            legal_ref = "Luật Quản lý thuế số 108/2025/QH15"
        else:
            legal_ref = "Luật Quản lý thuế số 38/2019/QH14, Điều 59 Khoản 2"

        breakdown.append({
            "giai_doan": f"{_format_date_vn(due)} → {_format_date_vn(pay)}",
            "so_ngay": days_late,
            "ty_le_ngay": "0,03%",
            "tien_cham_nop": round(penalty),
            "can_cu": legal_ref,
        })

    total_penalty = round(total_penalty)
    total_due = round(original_amount + total_penalty)

    tax_names = {
        "GTGT": "Thuế Giá trị gia tăng",
        "TNDN": "Thuế Thu nhập doanh nghiệp",
        "TNCN": "Thuế Thu nhập cá nhân",
    }

    return {
        "tax_type": tax_type,
        "tax_name": tax_names.get(tax_type, tax_type),
        "original_amount": original_amount,
        "due_date": _format_date_vn(due),
        "payment_date": _format_date_vn(pay),
        "days_late": days_late,
        "total_penalty": total_penalty,
        "total_due": total_due,
        "calculation_breakdown": breakdown,
        "formula": f"Tiền chậm nộp = {original_amount:,.0f} × tỷ lệ/ngày × {days_late} ngày = {total_penalty:,.0f} VNĐ",
        "legal_basis": (
            "Luật Quản lý thuế số 108/2025/QH15 (hiệu lực 01/07/2026): 0,03%/ngày. "
            "Luật Quản lý thuế số 38/2019/QH14, Điều 59 Khoản 2: 0,03%/ngày (từ 01/07/2016). "
            "Giai đoạn trước 01/07/2016: 0,05%/ngày."
        ),
        "note": (
            "Tiền chậm nộp được tính từ ngày tiếp theo ngày hết hạn đến ngày nộp vào NSNN. "
            "Số tiền trên là ước tính; cơ quan thuế sẽ ra thông báo chính thức."
        ),
    }


if __name__ == "__main__":
    mcp.run()
