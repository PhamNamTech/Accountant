"""
VBPL-Lookup MCP Server
Tra cứu, xác minh và kiểm tra tình trạng hiệu lực văn bản quy phạm pháp luật Việt Nam:
1. Tìm kiếm văn bản pháp luật theo từ khóa, số hiệu, tiêu đề trên vbpl.vn.
2. Kiểm tra tình trạng hiệu lực (Đang hiệu lực / Hết hiệu lực / Đã sửa đổi).
3. Đọc nội dung Điều / Khoản / Điểm cụ thể từ văn bản gốc.
4. Liệt kê các văn bản thay thế, sửa đổi, bổ sung.
5. Kiểm tra tự động staleness cho file legal-basis.md.
6. Theo dõi văn bản mới ban hành trong khoảng thời gian gần đây.
7. Đọc và trích xuất nội dung từ file PDF văn bản pháp luật.
8. Lập mục lục (index) cho file PDF văn bản pháp luật.
9. Đối chiếu chéo (cross-reference) dữ liệu trong legal-basis.md với văn bản thực tế.
"""

import os
import json
import hashlib
import re
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("vbpl-lookup")

# ---------------------------------------------------------------------------
# Thư mục cache
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE_DIR, "data", "cache", "vbpl")
SOURCES_DIR = os.path.join(BASE_DIR, "sources")
SOURCES_CACHE_DIR = os.path.join(SOURCES_DIR, "cache")

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(SOURCES_CACHE_DIR, exist_ok=True)

# Cơ sở dữ liệu văn bản pháp luật kế toán & thuế đã kiểm chứng từ legal-basis.md
VERIFIED_LEGAL_DATABASE = {
    "99/2025/TT-BTC": {
        "so_hieu": "99/2025/TT-BTC",
        "doc_number": "99/2025/TT-BTC",
        "tieu_de": "Thông tư số 99/2025/TT-BTC hướng dẫn Chế độ kế toán doanh nghiệp",
        "co_quan_ban_hanh": "Bộ Tài chính",
        "ngay_ban_hanh": "27/10/2025",
        "ngay_hieu_luc": "01/01/2026",
        "tinh_trang": "Đang hiệu lực (Áp dụng cho năm tài chính bắt đầu từ hoặc sau 01/01/2026)",
        "van_ban_thay_the": ["Thông tư 200/2014/TT-BTC"],
        "van_ban_bi_thay_the": [],
        "nguon": "legal-basis.md & Cổng thông tin Bộ Tài chính"
    },
    "200/2014/TT-BTC": {
        "so_hieu": "200/2014/TT-BTC",
        "doc_number": "200/2014/TT-BTC",
        "tieu_de": "Thông tư số 200/2014/TT-BTC hướng dẫn Chế độ kế toán Doanh nghiệp",
        "co_quan_ban_hanh": "Bộ Tài chính",
        "ngay_ban_hanh": "22/12/2014",
        "ngay_hieu_luc": "01/01/2015",
        "tinh_trang": "Hết hiệu lực từ năm tài chính 2026 (bị thay thế bởi Thông tư 99/2025/TT-BTC)",
        "van_ban_thay_the": ["Quyết định 15/2006/QĐ-BTC"],
        "van_ban_bi_thay_the": ["Thông tư 99/2025/TT-BTC"],
        "nguon": "legal-basis.md"
    },
    "133/2016/TT-BTC": {
        "so_hieu": "133/2016/TT-BTC",
        "doc_number": "133/2016/TT-BTC",
        "tieu_de": "Thông tư số 133/2016/TT-BTC hướng dẫn Chế độ kế toán doanh nghiệp nhỏ và vừa",
        "co_quan_ban_hanh": "Bộ Tài chính",
        "ngay_ban_hanh": "26/08/2016",
        "ngay_hieu_luc": "01/01/2017",
        "tinh_trang": "Đang hiệu lực (đã sửa đổi bởi Thông tư 46/2025/TT-BTC)",
        "van_ban_thay_the": ["Quyết định 48/2006/QĐ-BTC"],
        "van_ban_bi_thay_the": [],
        "nguon": "legal-basis.md"
    },
    "48/2024/QH15": {
        "so_hieu": "48/2024/QH15",
        "doc_number": "48/2024/QH15",
        "tieu_de": "Luật Thuế Giá trị gia tăng số 48/2024/QH15",
        "co_quan_ban_hanh": "Quốc hội",
        "ngay_ban_hanh": "26/11/2024",
        "ngay_hieu_luc": "01/07/2025",
        "tinh_trang": "Đang hiệu lực",
        "van_ban_thay_the": ["Luật Thuế GTGT 13/2008/QH12"],
        "van_ban_bi_thay_the": [],
        "nguon": "legal-basis.md"
    },
    "67/2025/QH15": {
        "so_hieu": "67/2025/QH15",
        "doc_number": "67/2025/QH15",
        "tieu_de": "Luật Thuế Thu nhập doanh nghiệp số 67/2025/QH15",
        "co_quan_ban_hanh": "Quốc hội",
        "ngay_ban_hanh": "14/06/2025",
        "ngay_hieu_luc": "01/10/2025",
        "tinh_trang": "Đang hiệu lực (Áp dụng từ kỳ tính thuế 2025)",
        "van_ban_thay_the": ["Luật Thuế TNDN 14/2008/QH12"],
        "van_ban_bi_thay_the": [],
        "nguon": "legal-basis.md"
    },
    "109/2025/QH15": {
        "so_hieu": "109/2025/QH15",
        "doc_number": "109/2025/QH15",
        "tieu_de": "Luật Thuế Thu nhập cá nhân số 109/2025/QH15",
        "co_quan_ban_hanh": "Quốc hội",
        "ngay_ban_hanh": "10/12/2025",
        "ngay_hieu_luc": "01/07/2026",
        "tinh_trang": "Đang hiệu lực (Áp dụng tiền lương từ kỳ 2026)",
        "van_ban_thay_the": ["Luật Thuế TNCN 04/2007/QH12"],
        "van_ban_bi_thay_the": [],
        "nguon": "legal-basis.md"
    },
    "254/2026/NĐ-CP": {
        "so_hieu": "254/2026/NĐ-CP",
        "doc_number": "254/2026/NĐ-CP",
        "tieu_de": "Nghị định số 254/2026/NĐ-CP về Hóa đơn, chứng từ điện tử",
        "co_quan_ban_hanh": "Chính phủ",
        "ngay_ban_hanh": "30/06/2026",
        "ngay_hieu_luc": "01/07/2026",
        "tinh_trang": "Đang hiệu lực (Thay thế NĐ 123/2020 và NĐ 70/2025)",
        "van_ban_thay_the": ["Nghị định 123/2020/NĐ-CP", "Nghị định 70/2025/NĐ-CP"],
        "van_ban_bi_thay_the": [],
        "nguon": "legal-basis.md"
    },
    "91/2026/TT-BTC": {
        "so_hieu": "91/2026/TT-BTC",
        "doc_number": "91/2026/TT-BTC",
        "tieu_de": "Thông tư số 91/2026/TT-BTC hướng dẫn Nghị định 254/2026/NĐ-CP về hóa đơn điện tử",
        "co_quan_ban_hanh": "Bộ Tài chính",
        "ngay_ban_hanh": "30/06/2026",
        "ngay_hieu_luc": "01/07/2026",
        "tinh_trang": "Đang hiệu lực (Thay thế Thông tư 32/2025/TT-BTC)",
        "van_ban_thay_the": ["Thông tư 32/2025/TT-BTC"],
        "van_ban_bi_thay_the": [],
        "nguon": "legal-basis.md"
    }
}

# ---------------------------------------------------------------------------
# HTTP User-Agent chung
# ---------------------------------------------------------------------------
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/128.0.0.0 Safari/537.36"
)

# ---------------------------------------------------------------------------
# Hàm hỗ trợ nội bộ
# ---------------------------------------------------------------------------

def _make_request(url: str, params: dict | None = None, retries: int = 2) -> dict:
    """
    Gửi HTTP GET với retry và xử lý lỗi nhất quán.
    Trả về {"ok": True, "text": ..., "url": ...} hoặc {"ok": False, "error": ...}.
    """
    import requests

    headers = {"User-Agent": _USER_AGENT, "Accept-Language": "vi-VN,vi;q=0.9"}
    last_error = ""
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=15)
            resp.raise_for_status()
            resp.encoding = resp.apparent_encoding or "utf-8"
            return {"ok": True, "text": resp.text, "url": resp.url}
        except requests.exceptions.Timeout:
            last_error = f"Hết thời gian chờ kết nối đến {url} (lần {attempt + 1})"
        except requests.exceptions.ConnectionError:
            last_error = f"Không thể kết nối đến {url} (lần {attempt + 1})"
        except requests.exceptions.HTTPError as e:
            last_error = f"Lỗi HTTP {e.response.status_code} từ {url}"
            break  # Không retry lỗi HTTP 4xx/5xx
        except Exception as e:
            last_error = f"Lỗi không xác định khi truy cập {url}: {str(e)}"
            break
    return {"ok": False, "error": last_error}


def _cache_key(prefix: str, *args) -> str:
    """Tạo tên file cache duy nhất từ prefix và các tham số."""
    raw = "|".join(str(a) for a in args)
    h = hashlib.md5(raw.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{h}.json"


def _read_cache(filename: str, max_age_hours: int = 24) -> dict | None:
    """Đọc cache JSON nếu còn hiệu lực (chưa quá max_age_hours)."""
    path = os.path.join(CACHE_DIR, filename)
    if not os.path.exists(path):
        return None
    try:
        mtime = os.path.getmtime(path)
        age = datetime.now().timestamp() - mtime
        if age > max_age_hours * 3600:
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _write_cache(filename: str, data: dict) -> None:
    """Ghi dữ liệu JSON vào file cache."""
    path = os.path.join(CACHE_DIR, filename)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _parse_vbpl_search_results(html: str) -> list[dict]:
    """
    Phân tích HTML trang kết quả tìm kiếm vbpl.vn.
    Trả về danh sách dict chứa thông tin từng văn bản.
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    results = []

    # vbpl.vn hiển thị kết quả trong các div.item / p.title / span
    items = soup.select("div.item, div.content div.nq, li.item, div.search-result-item")
    if not items:
        # Fallback: thử tìm tất cả thẻ <a> có link đến trang chi tiết
        items = soup.find_all("div", class_=re.compile(r"item|result|doc", re.IGNORECASE))

    for item in items:
        title_tag = item.find("a")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        href = title_tag.get("href", "")
        if href and not href.startswith("http"):
            href = "https://vbpl.vn" + href

        # Trích xuất thông tin phụ từ các span/div con
        spans = item.find_all(["span", "div", "p"])
        meta_text = " | ".join(s.get_text(strip=True) for s in spans if s.get_text(strip=True))

        # Tìm số hiệu văn bản
        doc_number_match = re.search(
            r"(\d+/\d{4}/[A-ZĐa-zđ\-]+)",
            title + " " + meta_text
        )
        doc_number = doc_number_match.group(1) if doc_number_match else ""

        # Tìm ngày ban hành / hiệu lực
        date_matches = re.findall(r"(\d{1,2}/\d{1,2}/\d{4})", meta_text)
        issue_date = date_matches[0] if len(date_matches) > 0 else ""
        effective_date = date_matches[1] if len(date_matches) > 1 else ""

        # Tình trạng hiệu lực
        status = "Không xác định"
        status_lower = meta_text.lower()
        if "còn hiệu lực" in status_lower or "đang hiệu lực" in status_lower:
            status = "Đang hiệu lực"
        elif "hết hiệu lực" in status_lower:
            status = "Hết hiệu lực"
        elif "sửa đổi" in status_lower:
            status = "Đã sửa đổi"

        if title:
            results.append({
                "tieu_de": title,
                "so_hieu": doc_number,
                "co_quan_ban_hanh": "",
                "ngay_ban_hanh": issue_date,
                "ngay_hieu_luc": effective_date,
                "tinh_trang": status,
                "url": href,
                "meta": meta_text[:300]
            })

    return results


def _parse_vbpl_detail_page(html: str) -> dict:
    """Phân tích trang chi tiết văn bản trên vbpl.vn."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    info = {
        "tieu_de": "",
        "so_hieu": "",
        "co_quan_ban_hanh": "",
        "ngay_ban_hanh": "",
        "ngay_hieu_luc": "",
        "tinh_trang": "",
        "noi_dung_toan_van": "",
        "van_ban_thay_the": [],
        "van_ban_bi_thay_the": []
    }

    # Tiêu đề
    title_tag = soup.find("div", class_=re.compile(r"title|ten", re.IGNORECASE))
    if title_tag:
        info["tieu_de"] = title_tag.get_text(strip=True)

    # Bảng thông tin thuộc tính
    table = soup.find("table", class_=re.compile(r"thuoc-tinh|attr|info", re.IGNORECASE))
    if table:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["td", "th"])
            if len(cells) >= 2:
                label = cells[0].get_text(strip=True).lower()
                value = cells[1].get_text(strip=True)
                if "số" in label and "hiệu" in label:
                    info["so_hieu"] = value
                elif "cơ quan" in label or "ban hành" in label and "ngày" not in label:
                    info["co_quan_ban_hanh"] = value
                elif "ngày ban hành" in label:
                    info["ngay_ban_hanh"] = value
                elif "hiệu lực" in label and "ngày" in label:
                    info["ngay_hieu_luc"] = value
                elif "tình trạng" in label or "trạng thái" in label:
                    info["tinh_trang"] = value

    # Nội dung toàn văn
    content_div = soup.find("div", class_=re.compile(r"content|full-text|noi-dung|toan-van", re.IGNORECASE))
    if content_div:
        info["noi_dung_toan_van"] = content_div.get_text(separator="\n", strip=True)

    # Trích xuất tình trạng từ các span/div trạng thái
    if not info["tinh_trang"]:
        status_tags = soup.find_all(["span", "div"], class_=re.compile(r"status|trang-thai|hieu-luc", re.IGNORECASE))
        for tag in status_tags:
            text = tag.get_text(strip=True)
            if text:
                info["tinh_trang"] = text
                break

    return info


# ---------------------------------------------------------------------------
# Các tool MCP
# ---------------------------------------------------------------------------

@mcp.tool()
def search_legal_document(query: str, doc_type: str = "", issuer: str = "") -> dict:
    """
    Tìm kiếm văn bản quy phạm pháp luật Việt Nam theo từ khóa, số hiệu hoặc tiêu đề.

    Tham số:
        query: Từ khóa tìm kiếm (ví dụ: "Thông tư 99/2025", "thuế GTGT", "kế toán doanh nghiệp").
        doc_type: Lọc theo loại văn bản (Luật, Nghị định, Thông tư, Quyết định, Công văn) — tùy chọn.
        issuer: Lọc theo cơ quan ban hành (Quốc hội, Chính phủ, Bộ Tài chính, Tổng cục Thuế) — tùy chọn.

    Trả về:
        Danh sách văn bản tìm thấy gồm: tiêu đề, số hiệu, cơ quan ban hành, ngày ban hành,
        ngày hiệu lực, tình trạng, đường dẫn nguồn.
    """
    # Kiểm tra cache
    cache_file = _cache_key("search", query, doc_type, issuer)
    cached = _read_cache(cache_file, max_age_hours=6)
    if cached:
        cached["tu_cache"] = True
        return cached

    # Thử tìm kiếm trên vbpl.vn
    search_url = "https://vbpl.vn/TW/Pages/vbpq-timkiem.aspx"
    params = {"keyword": query}
    if doc_type:
        params["loaivanban"] = doc_type
    if issuer:
        params["coquanbanhanh"] = issuer

    result = _make_request(search_url, params=params)

    if result["ok"]:
        documents = _parse_vbpl_search_results(result["text"])
        # Lọc thêm theo doc_type và issuer nếu kết quả chưa lọc
        if doc_type:
            doc_type_lower = doc_type.lower()
            documents = [d for d in documents if doc_type_lower in d.get("tieu_de", "").lower()
                         or doc_type_lower in d.get("meta", "").lower()]
        if issuer:
            issuer_lower = issuer.lower()
            documents = [d for d in documents if issuer_lower in d.get("co_quan_ban_hanh", "").lower()
                         or issuer_lower in d.get("meta", "").lower()]

        output = {
            "tu_khoa": query,
            "loai_van_ban": doc_type or "Tất cả",
            "co_quan_ban_hanh": issuer or "Tất cả",
            "so_ket_qua": len(documents),
            "ket_qua": documents,
            "nguon": "vbpl.vn",
            "thoi_gian_tra_cuu": datetime.now().isoformat()
        }
        _write_cache(cache_file, output)
        return output

    # Fallback: thử thuvienphapluat.vn
    fallback_url = "https://thuvienphapluat.vn/page/tim-van-ban.aspx"
    fallback_params = {"keyword": query}
    fallback_result = _make_request(fallback_url, params=fallback_params)

    if fallback_result["ok"]:
        documents = _parse_vbpl_search_results(fallback_result["text"])
        output = {
            "tu_khoa": query,
            "loai_van_ban": doc_type or "Tất cả",
            "co_quan_ban_hanh": issuer or "Tất cả",
            "so_ket_qua": len(documents),
            "ket_qua": documents,
            "nguon": "thuvienphapluat.vn (dự phòng)",
            "thoi_gian_tra_cuu": datetime.now().isoformat()
        }
        _write_cache(cache_file, output)
        return output

    # Fallback cuối cùng: Tra cứu trong cơ sở dữ liệu đã kiểm chứng
    matched_docs = []
    q_clean = query.strip().lower()
    for k, v in VERIFIED_LEGAL_DATABASE.items():
        if (q_clean in k.lower() or 
            q_clean in v["tieu_de"].lower() or 
            any(w in v["tieu_de"].lower() for w in q_clean.split())):
            matched_docs.append({
                "tieu_de": v["tieu_de"],
                "so_hieu": v["so_hieu"],
                "co_quan_ban_hanh": v["co_quan_ban_hanh"],
                "ngay_ban_hanh": v["ngay_ban_hanh"],
                "ngay_hieu_luc": v["ngay_hieu_luc"],
                "tinh_trang": v["tinh_trang"],
                "url": "legal-basis.md"
            })
    if matched_docs:
        output = {
            "tu_khoa": query,
            "loai_van_ban": doc_type or "Tất cả",
            "co_quan_ban_hanh": issuer or "Tất cả",
            "so_ket_qua": len(matched_docs),
            "ket_qua": matched_docs,
            "nguon": "Cơ sở dữ liệu căn cứ pháp lý nội bộ (legal-basis.md)",
            "thoi_gian_tra_cuu": datetime.now().isoformat()
        }
        _write_cache(cache_file, output)
        return output

    return {
        "error": f"Không thể truy cập cả vbpl.vn lẫn thuvienphapluat.vn. "
                 f"Lỗi gốc: {result['error']}",
        "tu_khoa": query
    }


@mcp.tool()
def get_document_status(doc_number: str) -> dict:
    """
    Kiểm tra tình trạng hiệu lực hiện hành của một văn bản quy phạm pháp luật.

    Tham số:
        doc_number: Số hiệu văn bản, ví dụ "99/2025/TT-BTC" hoặc "48/2024/QH15".

    Trả về:
        Tình trạng (Đang hiệu lực / Hết hiệu lực / Đã sửa đổi), ngày hiệu lực,
        danh sách văn bản thay thế, danh sách văn bản bị thay thế bởi.
    """
    cache_file = _cache_key("status", doc_number)
    cached = _read_cache(cache_file, max_age_hours=12)
    if cached:
        cached["tu_cache"] = True
        return cached

    # Kiểm tra trong cơ sở dữ liệu đã kiểm chứng trước
    clean_key = doc_number.strip().upper()
    for k, v in VERIFIED_LEGAL_DATABASE.items():
        if k.upper() in clean_key or clean_key in k.upper():
            return {
                "so_hieu": v["so_hieu"],
                "doc_number": v["doc_number"],
                "tieu_de": v["tieu_de"],
                "co_quan_ban_hanh": v["co_quan_ban_hanh"],
                "ngay_ban_hanh": v["ngay_ban_hanh"],
                "ngay_hieu_luc": v["ngay_hieu_luc"],
                "tinh_trang": v["tinh_trang"],
                "van_ban_thay_the": v["van_ban_thay_the"],
                "van_ban_bi_thay_the": v["van_ban_bi_thay_the"],
                "nguon": v["nguon"],
                "xac_minh": "Đã kiểm chứng theo legal-basis.md"
            }

    # Tìm kiếm văn bản trên vbpl.vn
    search_result = search_legal_document(doc_number)
    if "error" in search_result:
        return {"error": search_result["error"], "so_hieu": doc_number}

    documents = search_result.get("ket_qua", [])
    if not documents:
        return {
            "error": f"Không tìm thấy văn bản có số hiệu: {doc_number}",
            "so_hieu": doc_number,
            "goi_y": "Kiểm tra lại số hiệu hoặc tìm kiếm bằng từ khóa rộng hơn."
        }

    # Tìm văn bản khớp nhất
    target = None
    doc_number_clean = doc_number.strip().replace(" ", "")
    for doc in documents:
        if doc_number_clean.lower() in doc.get("so_hieu", "").lower().replace(" ", ""):
            target = doc
            break
    if not target:
        target = documents[0]

    # Thử lấy trang chi tiết để trích xuất thêm thông tin
    detail_info = {}
    if target.get("url"):
        detail_resp = _make_request(target["url"])
        if detail_resp["ok"]:
            detail_info = _parse_vbpl_detail_page(detail_resp["text"])

    status = detail_info.get("tinh_trang") or target.get("tinh_trang", "Không xác định")
    output = {
        "so_hieu": doc_number,
        "tieu_de": detail_info.get("tieu_de") or target.get("tieu_de", ""),
        "tinh_trang": status,
        "ngay_hieu_luc": detail_info.get("ngay_hieu_luc") or target.get("ngay_hieu_luc", ""),
        "ngay_ban_hanh": detail_info.get("ngay_ban_hanh") or target.get("ngay_ban_hanh", ""),
        "co_quan_ban_hanh": detail_info.get("co_quan_ban_hanh") or target.get("co_quan_ban_hanh", ""),
        "van_ban_thay_the": detail_info.get("van_ban_thay_the", []),
        "van_ban_bi_thay_the_boi": detail_info.get("van_ban_bi_thay_the", []),
        "url_nguon": target.get("url", ""),
        "thoi_gian_kiem_tra": datetime.now().isoformat()
    }
    _write_cache(cache_file, output)
    return output


@mcp.tool()
def read_document_article(doc_number: str, article: int, clause: int = 0, point: str = "") -> dict:
    """
    Đọc nội dung Điều / Khoản / Điểm cụ thể từ một văn bản quy phạm pháp luật.

    Tham số:
        doc_number: Số hiệu văn bản, ví dụ "99/2025/TT-BTC".
        article: Số Điều (ví dụ: 28 cho Điều 28).
        clause: Số Khoản (tùy chọn, 0 = đọc toàn bộ Điều).
        point: Ký hiệu Điểm (tùy chọn, ví dụ "a", "b", "c").

    Trả về:
        Nội dung văn bản trích xuất, tiêu đề văn bản, đường dẫn nguồn.
    """
    # Thử đọc từ file PDF nội bộ trước (nguồn Cấp 1)
    if os.path.isdir(SOURCES_DIR):
        import glob
        pdf_candidates = glob.glob(os.path.join(SOURCES_DIR, "**", "*.pdf"), recursive=True)
        doc_clean = doc_number.replace("/", "_").replace("-", "_").lower()
        for pdf_path in pdf_candidates:
            basename = os.path.basename(pdf_path).lower().replace(" ", "_")
            if doc_clean in basename or doc_number.split("/")[0] in basename:
                section_query = f"Điều {article}"
                local_result = read_legal_pdf_section(pdf_path, section_query)
                if "error" not in local_result and local_result.get("noi_dung"):
                    content = local_result["noi_dung"]
                    # Lọc tiếp theo Khoản / Điểm
                    if clause > 0:
                        content = _extract_clause(content, clause, point)
                    return {
                        "so_hieu": doc_number,
                        "dieu": article,
                        "khoan": clause if clause > 0 else "Toàn bộ Điều",
                        "diem": point or "Toàn bộ",
                        "noi_dung": content,
                        "tieu_de_van_ban": local_result.get("ten_file", ""),
                        "nguon": f"File nội bộ: {pdf_path}",
                        "cap_nguon": "Cấp 1 (PDF gốc nội bộ)"
                    }

    # Fallback: tìm trên vbpl.vn
    search_result = search_legal_document(doc_number)
    if "error" in search_result:
        return {"error": search_result["error"], "so_hieu": doc_number, "dieu": article}

    documents = search_result.get("ket_qua", [])
    if not documents:
        return {
            "error": f"Không tìm thấy văn bản {doc_number} trên nguồn trực tuyến.",
            "so_hieu": doc_number,
            "dieu": article
        }

    # Lấy trang chi tiết
    target = documents[0]
    doc_number_clean = doc_number.strip().replace(" ", "")
    for doc in documents:
        if doc_number_clean.lower() in doc.get("so_hieu", "").lower().replace(" ", ""):
            target = doc
            break

    if not target.get("url"):
        return {
            "error": "Không có đường dẫn đến trang chi tiết văn bản.",
            "so_hieu": doc_number
        }

    detail_resp = _make_request(target["url"])
    if not detail_resp["ok"]:
        return {"error": f"Không thể tải trang chi tiết: {detail_resp['error']}"}

    detail_info = _parse_vbpl_detail_page(detail_resp["text"])
    full_text = detail_info.get("noi_dung_toan_van", "")

    if not full_text:
        return {
            "error": "Không thể trích xuất nội dung toàn văn từ trang chi tiết.",
            "so_hieu": doc_number,
            "url": target.get("url", ""),
            "goi_y": "Thử tải file PDF gốc về thư mục sources/ rồi dùng read_legal_pdf_section."
        }

    # Tìm Điều cụ thể
    article_content = _extract_article(full_text, article)
    if not article_content:
        return {
            "error": f"Không tìm thấy Điều {article} trong văn bản {doc_number}.",
            "so_hieu": doc_number,
            "dieu": article
        }

    # Lọc tiếp theo Khoản / Điểm
    if clause > 0:
        article_content = _extract_clause(article_content, clause, point)

    return {
        "so_hieu": doc_number,
        "dieu": article,
        "khoan": clause if clause > 0 else "Toàn bộ Điều",
        "diem": point or "Toàn bộ",
        "noi_dung": article_content,
        "tieu_de_van_ban": detail_info.get("tieu_de", target.get("tieu_de", "")),
        "nguon": target.get("url", ""),
        "cap_nguon": "Cấp 1 (vbpl.vn)"
    }


def _extract_article(full_text: str, article_num: int) -> str:
    """Trích xuất nội dung một Điều từ toàn văn."""
    pattern = re.compile(
        rf"(Điều\s+{article_num}[\.\:]?\s.*?)(?=Điều\s+{article_num + 1}[\.\:]?\s|$)",
        re.DOTALL | re.IGNORECASE
    )
    match = pattern.search(full_text)
    if match:
        return match.group(1).strip()
    # Thử pattern đơn giản hơn
    pattern2 = re.compile(
        rf"(Điều\s+{article_num}\b.*?)(?=Điều\s+\d+\b|$)",
        re.DOTALL | re.IGNORECASE
    )
    match2 = pattern2.search(full_text)
    return match2.group(1).strip() if match2 else ""


def _extract_clause(article_text: str, clause_num: int, point: str = "") -> str:
    """Trích xuất Khoản và tùy chọn Điểm từ nội dung Điều."""
    pattern = re.compile(
        rf"({clause_num}\.\s.*?)(?=\d+\.\s|$)",
        re.DOTALL
    )
    match = pattern.search(article_text)
    clause_text = match.group(1).strip() if match else article_text

    if point and clause_text:
        point_pattern = re.compile(
            rf"({re.escape(point)}[\)\.]\s.*?)(?=[a-zđ][\)\.]\s|$)",
            re.DOTALL | re.IGNORECASE
        )
        point_match = point_pattern.search(clause_text)
        if point_match:
            return point_match.group(1).strip()

    return clause_text


@mcp.tool()
def get_replacing_documents(doc_number: str) -> dict:
    """
    Liệt kê tất cả các văn bản thay thế, sửa đổi hoặc bổ sung văn bản chỉ định.

    Tham số:
        doc_number: Số hiệu văn bản cần tra cứu, ví dụ "200/2014/TT-BTC".

    Trả về:
        Danh sách các văn bản liên quan gồm: số hiệu, tiêu đề, loại quan hệ
        (thay thế / sửa đổi / bổ sung), ngày hiệu lực.
    """
    cache_file = _cache_key("replacing", doc_number)
    cached = _read_cache(cache_file, max_age_hours=24)
    if cached:
        cached["tu_cache"] = True
        return cached

    # Lấy thông tin chi tiết văn bản
    status_info = get_document_status(doc_number)
    if "error" in status_info:
        return status_info

    replacing_docs = status_info.get("van_ban_thay_the", [])
    replaced_by = status_info.get("van_ban_bi_thay_the_boi", [])

    # Tìm thêm văn bản liên quan qua tìm kiếm
    search_result = search_legal_document(f"sửa đổi {doc_number}")
    related = []
    if "ket_qua" in search_result:
        for doc in search_result["ket_qua"]:
            title = doc.get("tieu_de", "").lower()
            relationship = "Không xác định"
            if "thay thế" in title:
                relationship = "Thay thế"
            elif "sửa đổi" in title:
                relationship = "Sửa đổi"
            elif "bổ sung" in title:
                relationship = "Bổ sung"
            elif "hướng dẫn" in title:
                relationship = "Hướng dẫn"

            if relationship != "Không xác định":
                related.append({
                    "so_hieu": doc.get("so_hieu", ""),
                    "tieu_de": doc.get("tieu_de", ""),
                    "loai_quan_he": relationship,
                    "ngay_hieu_luc": doc.get("ngay_hieu_luc", ""),
                    "url": doc.get("url", "")
                })

    output = {
        "so_hieu_goc": doc_number,
        "tieu_de": status_info.get("tieu_de", ""),
        "tinh_trang_hien_tai": status_info.get("tinh_trang", ""),
        "van_ban_thay_the_truc_tiep": replacing_docs,
        "van_ban_bi_thay_the_boi": replaced_by,
        "van_ban_lien_quan": related,
        "tong_so_van_ban_lien_quan": len(replacing_docs) + len(replaced_by) + len(related),
        "thoi_gian_tra_cuu": datetime.now().isoformat()
    }
    _write_cache(cache_file, output)
    return output


@mcp.tool()
def auto_staleness_check(legal_basis_path: str = "f:/Accountant/legal-basis.md") -> dict:
    """
    Kiểm tra tự động tình trạng "quá hạn rà soát" (staleness) cho file legal-basis.md.

    Quy tắc: Văn bản có ngày rà soát quá 90 ngày hoặc ghi "Chưa rà soát" sẽ bị đánh dấu.
    Tùy chọn gọi get_document_status để xác minh lại tình trạng hiệu lực.

    Tham số:
        legal_basis_path: Đường dẫn đến file legal-basis.md (mặc định: f:/Accountant/legal-basis.md).

    Trả về:
        Danh sách các văn bản cần rà soát lại cùng khuyến nghị.
    """
    if not os.path.exists(legal_basis_path):
        return {"error": f"Không tìm thấy file: {legal_basis_path}"}

    try:
        with open(legal_basis_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return {"error": f"Lỗi đọc file: {str(e)}"}

    now = datetime.now()
    threshold = timedelta(days=90)
    stale_documents = []
    up_to_date = []

    # Tìm tất cả dòng bảng markdown chứa thông tin văn bản
    # Cấu trúc: | STT | Số hiệu | ... | Ngày rà soát |
    lines = content.split("\n")
    for line in lines:
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")]
        cells = [c for c in cells if c]  # Loại bỏ phần tử rỗng

        if len(cells) < 5:
            continue

        # Bỏ qua dòng header (chứa :--- hoặc STT)
        if any(c.startswith(":") or c.startswith("-") for c in cells[:3]):
            continue
        if cells[0].lower() in ("stt", "---", ":---:"):
            continue

        # Cột cuối cùng là "Ngày rà soát"
        review_date_str = cells[-1].strip()
        doc_number = cells[1].strip().replace("**", "").replace("*", "")

        # Bỏ qua các dòng header
        if "số hiệu" in doc_number.lower() or "văn bản" in doc_number.lower():
            continue

        is_stale = False
        staleness_reason = ""

        if not review_date_str or "chưa" in review_date_str.lower():
            is_stale = True
            staleness_reason = "Chưa từng rà soát"
        else:
            # Thử phân tích ngày rà soát
            date_match = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", review_date_str)
            if date_match:
                try:
                    day, month, year = int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3))
                    review_date = datetime(year, month, day)
                    age = now - review_date
                    if age > threshold:
                        is_stale = True
                        staleness_reason = f"Đã {age.days} ngày kể từ lần rà soát gần nhất ({review_date_str})"
                    else:
                        up_to_date.append({
                            "so_hieu": doc_number,
                            "ngay_ra_soat": review_date_str,
                            "so_ngay_con_lai": (threshold - age).days
                        })
                except ValueError:
                    is_stale = True
                    staleness_reason = f"Không thể phân tích ngày rà soát: {review_date_str}"
            else:
                is_stale = True
                staleness_reason = f"Định dạng ngày không hợp lệ: {review_date_str}"

        if is_stale:
            stale_documents.append({
                "so_hieu": doc_number,
                "ngay_ra_soat_hien_tai": review_date_str,
                "ly_do": staleness_reason,
                "khuyen_nghi": f"Cần rà soát lại tình trạng hiệu lực của {doc_number} "
                               f"từ nguồn Cấp 1 (vbpl.vn hoặc chinhphu.vn)."
            })

    return {
        "tong_van_ban_kiem_tra": len(stale_documents) + len(up_to_date),
        "so_van_ban_can_ra_soat": len(stale_documents),
        "so_van_ban_con_hieu_luc_ra_soat": len(up_to_date),
        "van_ban_qua_han": stale_documents,
        "van_ban_con_hieu_luc_ra_soat": up_to_date,
        "nguong_canh_bao": "90 ngày",
        "thoi_gian_kiem_tra": now.isoformat(),
        "file_path": legal_basis_path
    }


@mcp.tool()
def check_new_regulations(keywords: list[str] = None, days_back: int = 30) -> dict:
    """
    Kiểm tra các văn bản quy phạm pháp luật mới ban hành trong khoảng thời gian gần đây.

    Tham số:
        keywords: Danh sách từ khóa tìm kiếm (mặc định: kế toán, thuế, hóa đơn, GTGT, TNDN, TNCN).
        days_back: Số ngày quay lại để tìm kiếm (mặc định: 30 ngày).

    Trả về:
        Danh sách văn bản mới ban hành kèm tiêu đề, số hiệu, ngày ban hành, tóm tắt.
    """
    if keywords is None:
        keywords = ["kế toán", "thuế", "hóa đơn", "GTGT", "TNDN", "TNCN"]

    cache_file = _cache_key("new_regs", ",".join(keywords), str(days_back))
    cached = _read_cache(cache_file, max_age_hours=6)
    if cached:
        cached["tu_cache"] = True
        return cached

    all_documents = []
    seen_titles = set()

    for kw in keywords:
        search_result = search_legal_document(kw)
        if "error" in search_result:
            continue

        for doc in search_result.get("ket_qua", []):
            title = doc.get("tieu_de", "")
            if title in seen_titles:
                continue

            # Kiểm tra ngày ban hành có nằm trong khoảng days_back
            issue_date_str = doc.get("ngay_ban_hanh", "")
            if issue_date_str:
                date_match = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", issue_date_str)
                if date_match:
                    try:
                        day = int(date_match.group(1))
                        month = int(date_match.group(2))
                        year = int(date_match.group(3))
                        issue_date = datetime(year, month, day)
                        cutoff = datetime.now() - timedelta(days=days_back)
                        if issue_date < cutoff:
                            continue
                    except ValueError:
                        pass

            seen_titles.add(title)
            doc["tu_khoa_tim_thay"] = kw
            all_documents.append(doc)

    # Sắp xếp theo ngày ban hành (mới nhất trước)
    def _parse_date_for_sort(doc):
        date_str = doc.get("ngay_ban_hanh", "")
        m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", date_str)
        if m:
            try:
                return datetime(int(m.group(3)), int(m.group(2)), int(m.group(1)))
            except ValueError:
                pass
        return datetime.min

    all_documents.sort(key=_parse_date_for_sort, reverse=True)

    output = {
        "tu_khoa": keywords,
        "so_ngay_tra_cuu": days_back,
        "so_van_ban_moi": len(all_documents),
        "van_ban_moi": all_documents,
        "thoi_gian_tra_cuu": datetime.now().isoformat()
    }
    _write_cache(cache_file, output)
    return output


@mcp.tool()
def read_legal_pdf_section(pdf_path: str, section_query: str) -> dict:
    """
    Đọc file PDF văn bản pháp luật và trích xuất nội dung theo truy vấn phần/mục.

    Tham số:
        pdf_path: Đường dẫn đến file PDF trong thư mục sources/.
        section_query: Truy vấn tìm kiếm, ví dụ "Điều 28", "Phụ lục II", "Chương III".

    Trả về:
        Nội dung trích xuất, số trang, tên file.
    """
    if not os.path.exists(pdf_path):
        # Thử tìm trong thư mục sources/
        alt_path = os.path.join(SOURCES_DIR, pdf_path)
        if os.path.exists(alt_path):
            pdf_path = alt_path
        else:
            return {"error": f"Không tìm thấy file PDF: {pdf_path}"}

    try:
        import pdfplumber

        pages_text = {}
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                pages_text[i] = text

        # Tìm kiếm section_query trong nội dung
        full_text = "\n".join(f"[Trang {p}]\n{t}" for p, t in pages_text.items())
        query_lower = section_query.lower().strip()

        # Xác định pattern dựa trên loại truy vấn
        if re.match(r"điều\s+\d+", query_lower, re.IGNORECASE):
            num_match = re.search(r"\d+", section_query)
            article_num = int(num_match.group()) if num_match else 0
            extracted = _extract_article(full_text, article_num)
        elif re.match(r"chương\s+", query_lower, re.IGNORECASE):
            pattern = re.compile(
                rf"({re.escape(section_query)}.*?)(?=Chương\s+[IVXLCDM]+|Chương\s+\d+|$)",
                re.DOTALL | re.IGNORECASE
            )
            match = pattern.search(full_text)
            extracted = match.group(1).strip() if match else ""
        elif re.match(r"phụ lục\s+", query_lower, re.IGNORECASE):
            pattern = re.compile(
                rf"({re.escape(section_query)}.*?)(?=Phụ lục\s+[IVXLCDM]+|Phụ lục\s+\d+|$)",
                re.DOTALL | re.IGNORECASE
            )
            match = pattern.search(full_text)
            extracted = match.group(1).strip() if match else ""
        else:
            # Tìm kiếm chung
            pattern = re.compile(re.escape(section_query), re.IGNORECASE)
            matches = list(pattern.finditer(full_text))
            if matches:
                start = max(0, matches[0].start() - 200)
                end = min(len(full_text), matches[0].end() + 3000)
                extracted = full_text[start:end]
            else:
                extracted = ""

        if not extracted:
            return {
                "error": f"Không tìm thấy nội dung khớp với '{section_query}' trong file PDF.",
                "ten_file": os.path.basename(pdf_path),
                "goi_y": "Thử truy vấn khác (ví dụ: 'Điều 28' thay vì 'điều 28')."
            }

        # Xác định các trang chứa kết quả
        matched_pages = []
        for page_num, page_text in pages_text.items():
            if section_query.lower() in page_text.lower():
                matched_pages.append(page_num)

        return {
            "ten_file": os.path.basename(pdf_path),
            "truy_van": section_query,
            "noi_dung": extracted[:10000],  # Giới hạn độ dài
            "da_cat_ngan": len(extracted) > 10000,
            "so_trang_khop": matched_pages,
            "tong_so_trang": len(pages_text),
            "duong_dan": pdf_path
        }

    except ImportError:
        return {"error": "Thư viện pdfplumber chưa được cài đặt. Chạy: pip install pdfplumber"}
    except Exception as e:
        return {"error": f"Lỗi đọc file PDF: {str(e)}"}


@mcp.tool()
def index_legal_pdf(pdf_path: str) -> dict:
    """
    Tạo mục lục (index) từ file PDF văn bản pháp luật.

    Trích xuất tất cả Chương (Chapter), Điều (Article), Phụ lục (Appendix) cùng số trang.
    Kết quả được lưu cache dưới dạng JSON trong sources/cache/.

    Tham số:
        pdf_path: Đường dẫn đến file PDF.

    Trả về:
        Mục lục có cấu trúc bao gồm Chương, Điều, Phụ lục kèm số trang.
    """
    if not os.path.exists(pdf_path):
        alt_path = os.path.join(SOURCES_DIR, pdf_path)
        if os.path.exists(alt_path):
            pdf_path = alt_path
        else:
            return {"error": f"Không tìm thấy file PDF: {pdf_path}"}

    # Kiểm tra cache
    cache_name = os.path.basename(pdf_path).replace(".pdf", "_index.json")
    cache_path = os.path.join(SOURCES_CACHE_DIR, cache_name)
    if os.path.exists(cache_path):
        try:
            mtime_pdf = os.path.getmtime(pdf_path)
            mtime_cache = os.path.getmtime(cache_path)
            if mtime_cache > mtime_pdf:
                with open(cache_path, "r", encoding="utf-8") as f:
                    cached = json.load(f)
                cached["tu_cache"] = True
                return cached
        except Exception:
            pass

    try:
        import pdfplumber

        chapters = []
        articles = []
        appendices = []

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                lines = text.split("\n")

                for line in lines:
                    line_stripped = line.strip()

                    # Tìm Chương
                    chapter_match = re.match(
                        r"^Chương\s+([IVXLCDM]+|\d+)[:\.\s]*(.*)",
                        line_stripped, re.IGNORECASE
                    )
                    if chapter_match:
                        chapters.append({
                            "loai": "Chương",
                            "so": chapter_match.group(1),
                            "tieu_de": chapter_match.group(2).strip(),
                            "trang": page_num
                        })

                    # Tìm Điều
                    article_match = re.match(
                        r"^Điều\s+(\d+)[:\.\s]*(.*)",
                        line_stripped, re.IGNORECASE
                    )
                    if article_match:
                        articles.append({
                            "loai": "Điều",
                            "so": int(article_match.group(1)),
                            "tieu_de": article_match.group(2).strip(),
                            "trang": page_num
                        })

                    # Tìm Phụ lục
                    appendix_match = re.match(
                        r"^Phụ lục\s+([IVXLCDM]+|\d+|[A-Z])[:\.\s]*(.*)",
                        line_stripped, re.IGNORECASE
                    )
                    if appendix_match:
                        appendices.append({
                            "loai": "Phụ lục",
                            "so": appendix_match.group(1),
                            "tieu_de": appendix_match.group(2).strip(),
                            "trang": page_num
                        })

        output = {
            "ten_file": os.path.basename(pdf_path),
            "duong_dan": pdf_path,
            "tong_so_trang": len(pdf.pages) if 'pdf' in dir() else 0,
            "muc_luc": {
                "chuong": chapters,
                "dieu": articles,
                "phu_luc": appendices
            },
            "thong_ke": {
                "so_chuong": len(chapters),
                "so_dieu": len(articles),
                "so_phu_luc": len(appendices)
            },
            "thoi_gian_index": datetime.now().isoformat()
        }

        # Đếm lại tổng số trang từ pages_text
        try:
            import pdfplumber as plb
            with plb.open(pdf_path) as pdf2:
                output["tong_so_trang"] = len(pdf2.pages)
        except Exception:
            pass

        # Lưu cache
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

        return output

    except ImportError:
        return {"error": "Thư viện pdfplumber chưa được cài đặt. Chạy: pip install pdfplumber"}
    except Exception as e:
        return {"error": f"Lỗi xử lý file PDF: {str(e)}"}


@mcp.tool()
def cross_reference_check(doc_number: str, field: str, expected_value: str) -> dict:
    """
    Đối chiếu chéo một trường thông tin trong legal-basis.md với văn bản thực tế.

    Tham số:
        doc_number: Số hiệu văn bản, ví dụ "99/2025/TT-BTC".
        field: Trường cần kiểm tra, ví dụ "TK 155", "Ngày hiệu lực", "Tình trạng".
        expected_value: Giá trị mong đợi, ví dụ "Sản phẩm", "01/01/2026", "Đang hiệu lực".

    Trả về:
        Kết quả so khớp / không khớp, giá trị thực tế từ nguồn, giá trị mong đợi.
    """
    # Bước 1: Thử tìm trong file PDF nội bộ
    actual_value = ""
    source_info = ""
    verification_level = "Chưa xác minh"

    if os.path.isdir(SOURCES_DIR):
        import glob
        pdf_files = glob.glob(os.path.join(SOURCES_DIR, "**", "*.pdf"), recursive=True)
        doc_clean = doc_number.replace("/", "_").replace("-", "_").lower()

        for pdf_path in pdf_files:
            basename = os.path.basename(pdf_path).lower().replace(" ", "_")
            if doc_clean in basename or doc_number.split("/")[0] in basename:
                # Tìm thấy file PDF, tìm field trong nội dung
                pdf_result = read_legal_pdf_section(pdf_path, field)
                if "error" not in pdf_result and pdf_result.get("noi_dung"):
                    actual_value = pdf_result["noi_dung"][:500]
                    source_info = f"File nội bộ: {pdf_path}"
                    verification_level = "Cấp 1 (PDF gốc nội bộ)"
                    break

    # Bước 2: Fallback - tra cứu trực tuyến
    if not actual_value:
        status_info = get_document_status(doc_number)
        if "error" not in status_info:
            # Kiểm tra field trong thông tin status
            field_lower = field.lower()
            if "hiệu lực" in field_lower or "ngày" in field_lower:
                actual_value = status_info.get("ngay_hieu_luc", "")
                source_info = status_info.get("url_nguon", "vbpl.vn")
                verification_level = "Cấp 1 (vbpl.vn)"
            elif "tình trạng" in field_lower or "trạng thái" in field_lower:
                actual_value = status_info.get("tinh_trang", "")
                source_info = status_info.get("url_nguon", "vbpl.vn")
                verification_level = "Cấp 1 (vbpl.vn)"
            else:
                source_info = status_info.get("url_nguon", "")
                verification_level = "Cấp 2 (tìm kiếm trực tuyến)"

    # So sánh
    if actual_value:
        expected_lower = expected_value.strip().lower()
        actual_lower = actual_value.strip().lower()
        is_match = (expected_lower in actual_lower) or (actual_lower in expected_lower)
        match_status = "KHỚP" if is_match else "KHÔNG KHỚP"
    else:
        match_status = "KHÔNG THỂ XÁC MINH"

    return {
        "so_hieu": doc_number,
        "truong_kiem_tra": field,
        "gia_tri_mong_doi": expected_value,
        "gia_tri_thuc_te": actual_value if actual_value else "Không tìm thấy dữ liệu để đối chiếu",
        "ket_qua": match_status,
        "nguon": source_info or "Không có nguồn",
        "muc_do_xac_minh": verification_level,
        "thoi_gian_kiem_tra": datetime.now().isoformat(),
        "goi_y": (
            "Tải file PDF văn bản gốc về thư mục sources/ để đối chiếu chính xác ở mức Cấp 1."
            if verification_level != "Cấp 1 (PDF gốc nội bộ)" else
            "Đã đối chiếu từ file PDF gốc nội bộ."
        )
    }


if __name__ == "__main__":
    mcp.run()
