"""
KetoanVN MCP Server
Chuyên phục vụ công tác kế toán Việt Nam:
1. Đọc và bóc tách dữ liệu Hóa đơn điện tử XML (chuẩn Thông tư 78/2021/TT-BTC và TT 32).
2. Tự động xuất bảng kê hóa đơn mua vào/bán ra ra file Excel chuẩn báo cáo thuế.
3. Tra cứu nhanh danh mục tài khoản kế toán chuẩn (Thông tư 200 & 133).
4. Đối soát giao dịch sao kê ngân hàng và sổ tiền gửi kế toán.
"""

import os
import glob
import xml.etree.ElementTree as ET
import pandas as pd
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ketoan-vn")

CHART_OF_ACCOUNTS = {
    "111": {"name": "Tiền mặt", "type": "Tài sản"},
    "1111": {"name": "Tiền Việt Nam", "type": "Tài sản"},
    "1112": {"name": "Ngoại tệ", "type": "Tài sản"},
    "112": {"name": "Tiền gửi ngân hàng", "type": "Tài sản"},
    "1121": {"name": "Tiền Việt Nam gửi ngân hàng", "type": "Tài sản"},
    "1122": {"name": "Ngoại tệ gửi ngân hàng", "type": "Tài sản"},
    "121": {"name": "Chứng khoán kinh doanh", "type": "Tài sản"},
    "128": {"name": "Đầu tư nắm giữ đến ngày đáo hạn", "type": "Tài sản"},
    "131": {"name": "Phải thu của khách hàng", "type": "Lưỡng tính (Tài sản/Nợ)"},
    "133": {"name": "Thuế GTGT được khấu trừ", "type": "Tài sản"},
    "1331": {"name": "Thuế GTGT được khấu trừ của hàng hóa, dịch vụ", "type": "Tài sản"},
    "1332": {"name": "Thuế GTGT được khấu trừ của tài sản cố định", "type": "Tài sản"},
    "141": {"name": "Tạm ứng", "type": "Tài sản"},
    "151": {"name": "Hàng mua đang đi đường", "type": "Tài sản"},
    "152": {"name": "Nguyên liệu, vật liệu", "type": "Tài sản"},
    "153": {"name": "Công cụ, dụng cụ", "type": "Tài sản"},
    # Tài khoản tập hợp chi phí và tính giá thành (Thông tư 200 & 133)
    "154": {"name": "Chi phí sản xuất, kinh doanh dở dang", "type": "Tài sản"},
    "1541": {"name": "Chi phí nguyên liệu, vật liệu trực tiếp (TT 133)", "type": "Tài sản"},
    "1542": {"name": "Chi phí nhân công trực tiếp (TT 133)", "type": "Tài sản"},
    "1543": {"name": "Chi phí máy thi công (TT 133)", "type": "Tài sản"},
    "1547": {"name": "Chi phí sản xuất chung (TT 133)", "type": "Tài sản"},
    "155": {"name": "Thành phẩm", "type": "Tài sản"},
    "1551": {"name": "Thành phẩm nhập kho", "type": "Tài sản"},
    "1552": {"name": "Thành phẩm bất động sản", "type": "Tài sản"},
    "156": {"name": "Hàng hóa", "type": "Tài sản"},
    "157": {"name": "Hàng gửi đi bán", "type": "Tài sản"},
    "211": {"name": "Tài sản cố định hữu hình", "type": "Tài sản"},
    "213": {"name": "Tài sản cố định vô hình", "type": "Tài sản"},
    "214": {"name": "Hao mòn tài sản cố định", "type": "Điều chỉnh giảm tài sản"},
    "242": {"name": "Chi phí trả trước", "type": "Tài sản"},
    "331": {"name": "Phải trả cho người bán", "type": "Lưỡng tính (Nợ/Tài sản)"},
    "333": {"name": "Thuế và các khoản phải nộp Nhà nước", "type": "Nợ phải trả"},
    "3331": {"name": "Thuế giá trị gia tăng phải nộp", "type": "Nợ phải trả"},
    "33311": {"name": "Thuế GTGT đầu ra", "type": "Nợ phải trả"},
    "3334": {"name": "Thuế thu nhập doanh nghiệp", "type": "Nợ phải trả"},
    "3335": {"name": "Thuế thu nhập cá nhân", "type": "Nợ phải trả"},
    "334": {"name": "Phải trả người lao động (Lương)", "type": "Nợ phải trả"},
    "338": {"name": "Phải trả, phải nộp khác (BHXH, BHYT, KPCĐ)", "type": "Nợ phải trả"},
    "3383": {"name": "Bảo hiểm xã hội", "type": "Nợ phải trả"},
    "3384": {"name": "Bảo hiểm y tế", "type": "Nợ phải trả"},
    "3386": {"name": "Bảo hiểm thất nghiệp", "type": "Nợ phải trả"},
    "341": {"name": "Vay và nợ thuê tài chính", "type": "Nợ phải trả"},
    "411": {"name": "Vốn đầu tư của chủ sở hữu", "type": "Vốn chủ sở hữu"},
    "421": {"name": "Lợi nhuận sau thuế chưa phân phối", "type": "Vốn chủ sở hữu"},
    "511": {"name": "Doanh thu bán hàng và cung cấp dịch vụ", "type": "Doanh thu"},
    "515": {"name": "Doanh thu hoạt động tài chính (Lãi tiền gửi, cổ tức...)", "type": "Doanh thu"},
    # Chi phí sản xuất tính giá thành (Thông tư 200)
    "621": {"name": "Chi phí nguyên liệu, vật liệu trực tiếp (TT 200)", "type": "Chi phí"},
    "622": {"name": "Chi phí nhân công trực tiếp (TT 200)", "type": "Chi phí"},
    "623": {"name": "Chi phí sử dụng máy thi công (TT 200)", "type": "Chi phí"},
    "627": {"name": "Chi phí sản xuất chung (TT 200)", "type": "Chi phí"},
    "6271": {"name": "Chi phí nhân viên phân xưởng", "type": "Chi phí"},
    "6272": {"name": "Chi phí vật liệu phân xưởng", "type": "Chi phí"},
    "6273": {"name": "Chi phí dụng cụ sản xuất", "type": "Chi phí"},
    "6274": {"name": "Chi phí khấu hao tài sản cố định", "type": "Chi phí"},
    "6277": {"name": "Chi phí dịch vụ mua ngoài", "type": "Chi phí"},
    "6278": {"name": "Chi phí bằng tiền khác", "type": "Chi phí"},
    "632": {"name": "Giá vốn hàng bán", "type": "Chi phí"},
    "635": {"name": "Chi phí tài chính (Lãi vay, lỗ tỷ giá...)", "type": "Chi phí"},
    "641": {"name": "Chi phí bán hàng", "type": "Chi phí"},
    "642": {"name": "Chi phí quản lý doanh nghiệp (TT200/TT133)", "type": "Chi phí"},
    "711": {"name": "Thu nhập khác", "type": "Thu nhập"},
    "811": {"name": "Chi phí khác", "type": "Chi phí"},
    "911": {"name": "Xác định kết quả kinh doanh", "type": "Trung gian kết chuyển"}
}

def _get_text(elem, path):
    node = elem.find(path)
    if node is not None and node.text:
        return node.text.strip()
    return ""

def _parse_single_xml(file_path: str):
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Xóa sạch namespace để tìm kiếm thẻ linh hoạt và chuẩn xác 100%
    for elem in root.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}', 1)[1]

    khhdon = _get_text(root, ".//TTChung/KHHDon") or _get_text(root, ".//KHHDon")
    shdon = _get_text(root, ".//TTChung/SHDon") or _get_text(root, ".//SHDon")
    nlap = _get_text(root, ".//TTChung/NLap") or _get_text(root, ".//NLap")

    ten_nban = _get_text(root, ".//NBan/Ten") or _get_text(root, ".//Seller/Name")
    mst_nban = _get_text(root, ".//NBan/MST") or _get_text(root, ".//Seller/TaxCode")
    dchi_nban = _get_text(root, ".//NBan/DChi") or _get_text(root, ".//Seller/Address")

    ten_nmua = _get_text(root, ".//NMua/Ten") or _get_text(root, ".//Buyer/Name")
    mst_nmua = _get_text(root, ".//NMua/MST") or _get_text(root, ".//Buyer/TaxCode")

    tgtcthue = _get_text(root, ".//TToan/TgTCThue") or _get_text(root, ".//TotalAmountWithoutVAT")
    tgtthue = _get_text(root, ".//TToan/TgTThue") or _get_text(root, ".//VATAmount")
    tgtttbso = _get_text(root, ".//TToan/TgTTTBSo") or _get_text(root, ".//TotalAmount")

    items_elems = root.findall(".//DSHHDV/HHDV")
    if not items_elems:
        items_elems = root.findall(".//HHDV")

    items = []
    for item in items_elems:
        thhdv = _get_text(item, "THHDV") or _get_text(item, "ItemName")
        dvt = _get_text(item, "DVT") or _get_text(item, "Unit")
        sluong = _get_text(item, "SLuong") or _get_text(item, "Quantity") or "0"
        dgia = _get_text(item, "DGia") or _get_text(item, "Price") or "0"
        thtien = _get_text(item, "ThTien") or _get_text(item, "Total") or "0"
        tsuat = _get_text(item, "TSuat") or _get_text(item, "VATRate") or ""
        
        if thhdv:
            items.append({
                "ten_hang": thhdv,
                "dvt": dvt,
                "so_luong": sluong,
                "don_gia": dgia,
                "thanh_tien": thtien,
                "thue_suat": tsuat
            })

    def safe_float(val):
        if not val:
            return 0.0
        try:
            return float(str(val).replace(',', ''))
        except Exception:
            return 0.0

    return {
        "file_name": os.path.basename(file_path),
        "ky_hieu": khhdon,
        "so_hoa_don": shdon,
        "ngay_lap": nlap,
        "nguoi_ban": {
            "ten": ten_nban,
            "mst": mst_nban,
            "dia_chi": dchi_nban
        },
        "nguoi_mua": {
            "ten": ten_nmua,
            "mst": mst_nmua
        },
        "tong_tien_chua_thue": safe_float(tgtcthue),
        "tien_thue_gtgt": safe_float(tgtthue),
        "tong_tien_thanh_toan": safe_float(tgtttbso),
        "chi_tiet_hang_hoa": items
    }

@mcp.tool()
def parse_vietnamese_invoice_xml(file_path: str) -> dict:
    if not os.path.exists(file_path):
        return {"error": f"Không tìm thấy file: {file_path}"}
    try:
        return _parse_single_xml(file_path)
    except Exception as e:
        return {"error": f"Lỗi đọc file XML: {str(e)}"}

@mcp.tool()
def batch_export_invoices_to_excel(folder_path: str, output_excel_path: str) -> dict:
    if not os.path.isdir(folder_path):
        return {"error": f"Thư mục không tồn tại: {folder_path}"}

    xml_files = glob.glob(os.path.join(folder_path, "**", "*.xml"), recursive=True)
    if not xml_files:
        return {"error": f"Không tìm thấy file .xml nào trong thư mục: {folder_path}"}

    summary_list = []
    items_list = []

    for f in xml_files:
        try:
            data = _parse_single_xml(f)
            summary_list.append({
                "Tên file": data["file_name"],
                "Ký hiệu HĐ": data["ky_hieu"],
                "Số HĐ": data["so_hoa_don"],
                "Ngày lập": data["ngay_lap"],
                "MST Người bán": data["nguoi_ban"]["mst"],
                "Tên Người bán": data["nguoi_ban"]["ten"],
                "MST Người mua": data["nguoi_mua"]["mst"],
                "Tên Người mua": data["nguoi_mua"]["ten"],
                "Doanh số chưa thuế": data["tong_tien_chua_thue"],
                "Tiền thuế GTGT": data["tien_thue_gtgt"],
                "Tổng tiền thanh toán": data["tong_tien_thanh_toan"]
            })

            for item in data["chi_tiet_hang_hoa"]:
                items_list.append({
                    "Số HĐ": data["so_hoa_don"],
                    "Ký hiệu": data["ky_hieu"],
                    "Ngày lập": data["ngay_lap"],
                    "Người bán": data["nguoi_ban"]["ten"],
                    "Tên hàng hóa, dịch vụ": item["ten_hang"],
                    "Đơn vị tính": item["dvt"],
                    "Số lượng": item["so_luong"],
                    "Đơn giá": item["don_gia"],
                    "Thành tiền": item["thanh_tien"],
                    "Thuế suất": item["thue_suat"]
                })
        except Exception:
            continue

    df_summary = pd.DataFrame(summary_list)
    df_items = pd.DataFrame(items_list)

    os.makedirs(os.path.dirname(os.path.abspath(output_excel_path)), exist_ok=True)
    with pd.ExcelWriter(output_excel_path, engine="xlsxwriter") as writer:
        df_summary.to_excel(writer, sheet_name="Bang_Ke_Tong_Hop", index=False)
        df_items.to_excel(writer, sheet_name="Chi_Tiet_Hang_Hoa", index=False)

    return {
        "status": "success",
        "total_invoices_processed": len(summary_list),
        "total_items_processed": len(items_list),
        "output_excel": output_excel_path
    }

@mcp.tool()
def lookup_accounting_account(query: str) -> dict:
    query_lower = query.lower().strip()
    results = {}
    for code, info in CHART_OF_ACCOUNTS.items():
        if query_lower in code or query_lower in info["name"].lower():
            results[code] = info
    return {"results": results, "count": len(results)}

@mcp.tool()
def parse_vietnamese_invoice_pdf(pdf_path: str) -> dict:
    """
    Bóc tách thông tin từ file Hóa đơn điện tử PDF:
    Số hóa đơn, ký hiệu, ngày lập, thông tin bên bán, bên mua, tổng tiền hàng, thuế GTGT, tổng thanh toán.
    """
    if not os.path.exists(pdf_path):
        return {"error": f"Không tìm thấy file: {pdf_path}"}
    try:
        import pdfplumber
        import re

        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"

        so_hd_m = re.search(r"S[oó]\s*(?:h[oó]a\s*[dđ][oơ]n|hđ)[:\s]*([0-9]+)", text, re.IGNORECASE)
        ky_hieu_m = re.search(r"K[yý]\s*hi[eệ]u[:\s]*([A-Z0-9]+)", text, re.IGNORECASE)
        ngay_lap_m = re.search(r"Ng[aà]y\s*l[aậ]p[:\s]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{4})", text, re.IGNORECASE)

        mst_matches = re.findall(r"M[aã]\s*s[oó]\s*thu[eế][:.\s]*([0-9]{10}(?:-[0-9]{3})?)", text, re.IGNORECASE)
        mst_seller = mst_matches[0] if len(mst_matches) > 0 else ""
        mst_buyer = mst_matches[1] if len(mst_matches) > 1 else ""

        tong_tien_m = re.search(r"T[oổ]ng\s*ti[eề]n\s*thanh\s*to[aá]n[:\s]*([\d,.]+)", text, re.IGNORECASE)
        tien_thue_m = re.search(r"Ti[eề]n\s*thu[eế][:.\s]*([\d,.]+)", text, re.IGNORECASE)
        tien_hang_m = re.search(r"C[oộ]ng\s*ti[eề]n\s*h[aà]ng[:\s]*([\d,.]+)", text, re.IGNORECASE)

        return {
            "file_name": os.path.basename(pdf_path),
            "so_hoa_don": so_hd_m.group(1) if so_hd_m else "",
            "ky_hieu": ky_hieu_m.group(1) if ky_hieu_m else "",
            "ngay_lap": ngay_lap_m.group(1) if ngay_lap_m else "",
            "mst_nguoi_ban": mst_seller,
            "mst_nguoi_mua": mst_buyer,
            "tien_hang": tien_hang_m.group(1) if tien_hang_m else "",
            "tien_thue": tien_thue_m.group(1) if tien_thue_m else "",
            "tong_thanh_toan": tong_tien_m.group(1) if tong_tien_m else ""
        }
    except Exception as e:
        return {"error": f"Lỗi đọc file PDF: {str(e)}"}

@mcp.tool()
def verify_beancount_ledger(ledger_path: str) -> dict:
    """
    Tải và kiểm tra tính cân đối kép của Sổ cái Beancount (Double-entry Plaintext Accounting).
    Trả về số lượng bút toán, các lỗi mất cân đối (nếu có) và danh sách tài khoản đã sử dụng.
    """
    if not os.path.exists(ledger_path):
        return {"error": f"Không tìm thấy file ledger: {ledger_path}"}
    try:
        from beancount import loader
        entries, errors, options = loader.load_file(ledger_path)
        return {
            "status": "valid" if len(errors) == 0 else "errors_found",
            "total_entries": len(entries),
            "errors": [str(err) for err in errors],
            "operating_currency": options.get("operating_currency", []),
            "accounts_count": len([e for e in entries if hasattr(e, 'account')])
        }
    except Exception as e:
        return {"error": f"Lỗi kiểm tra ledger: {str(e)}"}

@mcp.tool()
def calculate_product_cost(
    product_name: str,
    d_dau_ky: float,
    cp_nvl_truc_tiep: float,
    cp_nhan_cong_truc_tiep: float,
    cp_san_xuat_chung: float,
    d_cuoi_ky: float,
    sl_hoan_thanh: float,
    phe_lieu_thu_hoi: float = 0.0,
    regime: str = "TT99"
) -> dict:
    """
    Tính giá thành sản xuất sản phẩm (Phương pháp giản đơn/trực tiếp):
    Công thức: Z = D_dau + (CP_NVL + CP_NC + CP_SXC) - D_cuoi - Phe_lieu
    Giá thành đơn vị: z = Z / SL_hoan_thanh
    regime: 'TT99' (mặc định), 'TT200' hoặc 'TT133'
    """
    if sl_hoan_thanh <= 0:
        return {"error": "Số lượng thành phẩm hoàn thành phải lớn hơn 0"}

    tong_chi_phi_phat_sinh = cp_nvl_truc_tiep + cp_nhan_cong_truc_tiep + cp_san_xuat_chung
    tong_gia_thanh_z = d_dau_ky + tong_chi_phi_phat_sinh - d_cuoi_ky - phe_lieu_thu_hoi
    gia_thanh_don_vi_z = tong_gia_thanh_z / sl_hoan_thanh

    co_cau = {}
    if tong_chi_phi_phat_sinh > 0:
        co_cau = {
            "ty_trong_nvl": round((cp_nvl_truc_tiep / tong_chi_phi_phat_sinh) * 100, 2),
            "ty_trong_nhan_cong": round((cp_nhan_cong_truc_tiep / tong_chi_phi_phat_sinh) * 100, 2),
            "ty_trong_sx_chung": round((cp_san_xuat_chung / tong_chi_phi_phat_sinh) * 100, 2)
        }

    regime_key = regime.upper().replace(" ", "").replace("_", "")
    if "133" in regime_key:
        che_do_str = "Thông tư 133/2016/TT-BTC"
        tk_nhap_kho = "155"
        ten_sp = "Thành phẩm"
        but_toan_chi_phi = [
            {"khoan_muc": "Chi phí NVL trực tiếp", "tk": "1541", "so_tien": cp_nvl_truc_tiep},
            {"khoan_muc": "Chi phí Nhân công trực tiếp", "tk": "1542", "so_tien": cp_nhan_cong_truc_tiep},
            {"khoan_muc": "Chi phí Sản xuất chung", "tk": "1547", "so_tien": cp_san_xuat_chung}
        ]
    elif "200" in regime_key:
        che_do_str = "Thông tư 200/2014/TT-BTC"
        tk_nhap_kho = "1551"
        ten_sp = "Thành phẩm"
        but_toan_chi_phi = [
            {"no": "154", "co": "621", "so_tien": cp_nvl_truc_tiep},
            {"no": "154", "co": "622", "so_tien": cp_nhan_cong_truc_tiep},
            {"no": "154", "co": "627", "so_tien": cp_san_xuat_chung}
        ]
    else:
        che_do_str = "Thông tư 99/2025/TT-BTC"
        tk_nhap_kho = "155"  # TT 99 bãi bỏ tiểu khoản 1551/1557 cứng, dùng TK 155 Sản phẩm
        ten_sp = "Sản phẩm"
        but_toan_chi_phi = [
            {"no": "154", "co": "621", "so_tien": cp_nvl_truc_tiep},
            {"no": "154", "co": "622", "so_tien": cp_nhan_cong_truc_tiep},
            {"no": "154", "co": "627", "so_tien": cp_san_xuat_chung}
        ]

    return {
        "san_pham": product_name,
        "che_do_ke_toan": che_do_str,
        "so_luong_hoan_thanh": sl_hoan_thanh,
        "do_dang_dau_ky": d_dau_ky,
        "chi_phi_phat_sinh_trong_ky": {
            "nvl_truc_tiep": cp_nvl_truc_tiep,
            "nhan_cong_truc_tiep": cp_nhan_cong_truc_tiep,
            "san_xuat_chung": cp_san_xuat_chung,
            "tong_phat_sinh": tong_chi_phi_phat_sinh
        },
        "do_dang_cuoi_ky": d_cuoi_ky,
        "phe_lieu_thu_hoi": phe_lieu_thu_hoi,
        "tong_gia_thanh_Z": tong_gia_thanh_z,
        "gia_thanh_don_vi_z": round(gia_thanh_don_vi_z, 2),
        "co_cau_chi_phi_phan_tram": co_cau,
        "but_toan_dinh_khoan": {
            "tap_hop_hoac_ket_chuyen": but_toan_chi_phi,
            "nhap_kho": {
                "no": tk_nhap_kho,
                "co": "154",
                "so_tien": tong_gia_thanh_z,
                "dien_giai": f"Nhập kho {ten_sp.lower()} {sl_hoan_thanh} {product_name} theo giá thành sản xuất thực tế"
            }
        }
    }

@mcp.tool()
def allocate_overhead_costs(
    total_overhead: float,
    products: list[dict],
    criteria: str = "nvl"
) -> dict:
    """
    Phân bổ Chi phí sản xuất chung (TK 627) cho nhiều đối tượng sản phẩm.
    criteria:
      - 'nvl': theo chi phí nguyên vật liệu trực tiếp (621)
      - 'nhan_cong': theo chi phí nhân công trực tiếp (622)
      - 'so_luong': theo số lượng sản phẩm sản xuất
    products: danh sách các sản phẩm [{'name': 'SP A', 'base_value': 1000000}, ...]
    """
    total_base = sum(p.get("base_value", 0) for p in products)
    if total_base <= 0:
        return {"error": "Tổng tiêu thức phân bổ phải lớn hơn 0"}

    rate = total_overhead / total_base
    results = []
    total_allocated = 0.0

    for p in products:
        allocated = round(p.get("base_value", 0) * rate, 2)
        total_allocated += allocated
        results.append({
            "san_pham": p.get("name"),
            "gia_tri_tieu_thuc": p.get("base_value"),
            "he_so_phan_bo": round((p.get("base_value", 0) / total_base) * 100, 2),
            "chi_phi_sxc_phan_bo": allocated
        })

    return {
        "tong_chi_phi_sxc_can_phan_bo": total_overhead,
        "tieu_thuc_phan_bo": criteria,
        "he_so_phan_bo_don_vi": rate,
        "ket_qua_phan_bo": results,
        "tong_da_phan_bo": total_allocated
    }

@mcp.tool()
def export_cost_sheet_excel(
    output_excel_path: str,
    product_name: str,
    ky_tinh_gia_thanh: str,
    sl_hoan_thanh: float,
    d_dau_ky_dict: dict,
    phat_sinh_dict: dict,
    d_cuoi_ky_dict: dict
) -> dict:
    """
    Xuất file Excel 'THẺ TÍNH GIÁ THÀNH SẢN PHẨM' chuẩn mẫu kế toán Việt Nam.
    Bao gồm các khoản mục: NVL trực tiếp, Nhân công trực tiếp, Chi phí SX chung.
    """
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

    os.makedirs(os.path.dirname(os.path.abspath(output_excel_path)), exist_ok=True)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "The_Tinh_Gia_Thanh"

    ws["A1"] = "DOANH NGHIỆP SẢN XUẤT"
    ws["A1"].font = Font(name="Times New Roman", size=10, bold=True)
    ws["A2"] = "Bộ phận: Kế toán Giá thành"
    ws["A2"].font = Font(name="Times New Roman", size=9, italic=True)

    ws["A4"] = "THẺ TÍNH GIÁ THÀNH SẢN PHẨM"
    ws["A4"].font = Font(name="Times New Roman", size=16, bold=True, color="002060")
    ws["A4"].alignment = Alignment(horizontal="center")
    ws.merge_cells("A4:G4")

    ws["A5"] = f"Tên sản phẩm: {product_name} | Số lượng hoàn thành: {sl_hoan_thanh:,.0f} | Kỳ tính: {ky_tinh_gia_thanh}"
    ws["A5"].font = Font(name="Times New Roman", size=11, italic=True)
    ws["A5"].alignment = Alignment(horizontal="center")
    ws.merge_cells("A5:G5")

    headers = [
        "STT", "Khoản mục chi phí", "Dở dang đầu kỳ (D_đk)", 
        "Chi phí phát sinh (C)", "Dở dang cuối kỳ (D_ck)", 
        "Tổng giá thành (Z)", "Giá thành đơn vị (z)"
    ]
    header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    header_font = Font(name="Times New Roman", size=10, bold=True, color="FFFFFF")

    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=7, column=col_idx, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    items = [
        ("1", "Chi phí NVL trực tiếp (TK 621)", d_dau_ky_dict.get("nvl", 0), phat_sinh_dict.get("nvl", 0), d_cuoi_ky_dict.get("nvl", 0)),
        ("2", "Chi phí Nhân công trực tiếp (TK 622)", d_dau_ky_dict.get("nc", 0), phat_sinh_dict.get("nc", 0), d_cuoi_ky_dict.get("nc", 0)),
        ("3", "Chi phí Sản xuất chung (TK 627)", d_dau_ky_dict.get("sxc", 0), phat_sinh_dict.get("sxc", 0), d_cuoi_ky_dict.get("sxc", 0))
    ]

    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )

    for idx, (stt, name, d_dk, c_ps, d_ck) in enumerate(items, start=8):
        ws.cell(row=idx, column=1, value=stt).alignment = Alignment(horizontal="center")
        ws.cell(row=idx, column=2, value=name)
        ws.cell(row=idx, column=3, value=d_dk).number_format = '#,##0'
        ws.cell(row=idx, column=4, value=c_ps).number_format = '#,##0'
        ws.cell(row=idx, column=5, value=d_ck).number_format = '#,##0'
        
        ws.cell(row=idx, column=6, value=f"=C{idx}+D{idx}-E{idx}").number_format = '#,##0'
        ws.cell(row=idx, column=7, value=f"=F{idx}/{sl_hoan_thanh}").number_format = '#,##0'

        for c in range(1, 8):
            cell = ws.cell(row=idx, column=c)
            cell.font = Font(name="Times New Roman", size=10)
            cell.border = thin_border
            if c >= 3:
                cell.alignment = Alignment(horizontal="right")

    total_row = 11
    ws.cell(row=total_row, column=2, value="TỔNG CỘNG GIÁ THÀNH").font = Font(name="Times New Roman", size=11, bold=True)
    for c in range(3, 8):
        cell = ws.cell(row=total_row, column=c)
        col_letter = openpyxl.utils.get_column_letter(c)
        cell.value = f"=SUM({col_letter}8:{col_letter}10)"
        cell.font = Font(name="Times New Roman", size=11, bold=True, color="C00000")
        cell.number_format = '#,##0'
        cell.alignment = Alignment(horizontal="right")

    col_widths = [8, 38, 20, 22, 20, 22, 20]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

    wb.save(output_excel_path)
    return {
        "status": "success",
        "output_excel": output_excel_path,
        "product_name": product_name,
        "sl_hoan_thanh": sl_hoan_thanh
    }

if __name__ == "__main__":
    mcp.run()

