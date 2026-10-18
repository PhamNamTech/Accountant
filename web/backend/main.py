"""
FastAPI Backend cho Hệ Thống Kế Toán AI Việt Nam (Vietnam Accounting Suite)
Tích hợp trực tiếp các công cụ kế toán chuyên sâu:
- Tra cứu tài khoản TT 99/2025, TT 200/2014, TT 133/2016
- Bóc tách hóa đơn điện tử XML (TT 78) & PDF
- Tính giá thành sản phẩm Z, z & phân bổ chi phí SXC theo VAS 02
- Quản lý sổ Nhật ký chung (SQLite) & Sổ cái Beancount
- Đối soát sao kê ngân hàng (Vietcombank) với Sổ TK 112
- Cơ sở pháp lý và ma trận tra cứu chuẩn hóa
"""

import os
import sys
import glob
import json
import sqlite3
import shutil
import tempfile
import re
import threading
import io
import zipfile
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Thêm đường dẫn gốc vào sys.path để import tools.ketoan_server
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from tools.ketoan_server import (
    lookup_accounting_account,
    parse_vietnamese_invoice_xml,
    parse_vietnamese_invoice_pdf,
    verify_beancount_ledger,
    calculate_product_cost,
    allocate_overhead_costs,
    export_cost_sheet_excel,
    batch_export_invoices_to_excel,
    CHART_OF_ACCOUNTS_TT99,
    CHART_OF_ACCOUNTS_TT200,
    CHART_OF_ACCOUNTS_TT133,
)

app = FastAPI(
    title="Vietnam Accounting AI Suite API",
    description="API hệ thống quản lý, hạch toán và tính giá thành chuẩn mực kế toán Việt Nam",
    version="1.0.0",
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(BASE_DIR, "data", "database", "ketoan.db")
BEANCOUNT_PATH = os.path.join(BASE_DIR, "data", "database", "so_cai.beancount")
SAMPLE_XML_DIR = os.path.join(BASE_DIR, "tests", "test_data")
SAMPLE_INVOICE_DIR = os.path.join(BASE_DIR, "data", "chung_tu", "hoa_don_mua_vao", "2026-07")
SAMPLE_BANK_FILE = os.path.join(BASE_DIR, "data", "ngan_hang", "sao_ke", "Sao ke VCB - 20261012.xls")


def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS nhat_ky_chung (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ngay_ghi_so TEXT NOT NULL,
            so_chung_tu TEXT NOT NULL,
            ngay_chung_tu TEXT NOT NULL,
            dien_giai TEXT NOT NULL,
            tk_no TEXT NOT NULL,
            tk_co TEXT NOT NULL,
            so_tien REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


init_db()


# ==========================================
# 1. API HỆ THỐNG & TỔNG QUAN
# ==========================================
@app.get("/api/health")
def get_health():
    db_ok = os.path.exists(DB_PATH)
    beancount_ok = os.path.exists(BEANCOUNT_PATH)
    vcb_user = os.environ.get("VCB_USERNAME", "")
    return {
        "status": "healthy",
        "online": True,
        "timestamp": datetime.now().isoformat(),
        "database": {"connected": db_ok, "path": DB_PATH},
        "beancount": {"exists": beancount_ok, "path": BEANCOUNT_PATH},
        "vcb_configured": bool(vcb_user and os.environ.get("VCB_PASSWORD")),
        "vcb_username": f"{vcb_user[:3]}***" if vcb_user else "",
        "regimes_supported": ["TT99/2025/TT-BTC", "TT200/2014/TT-BTC", "TT133/2016/TT-BTC"],
    }


# ==========================================
# 2. API TRA CỨU HỆ THỐNG TÀI KHOẢN
# ==========================================
@app.get("/api/accounts")
@app.get("/api/accounts/lookup")
def api_lookup_accounts(
    query: str = Query("", description="Số hiệu hoặc tên tài khoản"),
    regime: str = Query("TT99", description="Chế độ kế toán: TT99, TT200, hoặc TT133"),
):
    try:
        res = lookup_accounting_account(query, regime=regime)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/accounts/all")
def api_get_all_accounts(regime: str = Query("TT99")):
    regime_key = regime.upper().replace(" ", "").replace("_", "")
    if "133" in regime_key:
        chart = CHART_OF_ACCOUNTS_TT133
        title = "Thông tư 133/2016/TT-BTC (Doanh nghiệp nhỏ và vừa)"
    elif "200" in regime_key:
        chart = CHART_OF_ACCOUNTS_TT200
        title = "Thông tư 200/2014/TT-BTC (Năm tài chính trước 2026)"
    else:
        chart = CHART_OF_ACCOUNTS_TT99
        title = "Thông tư 99/2025/TT-BTC (Từ năm tài chính 2026)"

    accounts_list = [{"code": k, **v} for k, v in chart.items()]
    return {
        "regime": title,
        "total_accounts": len(accounts_list),
        "accounts": accounts_list,
    }


# ==========================================
# 3. API BÓC TÁCH HÓA ĐƠN XML & PDF
# ==========================================
@app.get("/api/invoices/samples")
def get_sample_invoices():
    samples = []
    # Quét thư mục test_data
    if os.path.exists(SAMPLE_XML_DIR):
        for f in glob.glob(os.path.join(SAMPLE_XML_DIR, "*.*")):
            ext = os.path.splitext(f)[1].lower()
            if ext in [".xml", ".pdf"]:
                samples.append({
                    "name": os.path.basename(f),
                    "path": f,
                    "type": "XML" if ext == ".xml" else "PDF",
                    "folder": "test_data",
                })
    # Quét thêm 10 hóa đơn thực tế từ data/chung_tu
    if os.path.exists(SAMPLE_INVOICE_DIR):
        for f in glob.glob(os.path.join(SAMPLE_INVOICE_DIR, "*.xml"))[:8]:
            samples.append({
                "name": os.path.basename(f),
                "path": f,
                "type": "XML",
                "folder": "2026-07",
            })
    return {"samples": samples}


@app.post("/api/invoices/load-sample")
def load_sample_invoice(path: str = Query(...)):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File mẫu không tồn tại")
    ext = os.path.splitext(path)[1].lower()
    if ext == ".xml":
        res = parse_vietnamese_invoice_xml(path)
        return {"type": "XML", "data": res}
    elif ext == ".pdf":
        res = parse_vietnamese_invoice_pdf(path)
        return {"type": "PDF", "data": res}
    else:
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file .xml hoặc .pdf")


@app.post("/api/invoices/parse-xml")
async def parse_xml_upload(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".xml"):
        raise HTTPException(status_code=400, detail="Vui lòng tải lên file định dạng XML")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        data = parse_vietnamese_invoice_xml(tmp_path)
        data["file_name"] = file.filename
        return data
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.post("/api/invoices/parse-pdf")
async def parse_pdf_upload(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Vui lòng tải lên file định dạng PDF")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        data = parse_vietnamese_invoice_pdf(tmp_path)
        data["file_name"] = file.filename
        return data
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# ==========================================
# 4. API KẾ TOÁN GIÁ THÀNH & PHÂN BỔ SXC (VAS 02)
# ==========================================
class ProductCostRequest(BaseModel):
    product_name: str = "Bàn gỗ sồi"
    d_dau_ky: float = 10000000.0
    cp_nvl_truc_tiep: float = 50000000.0
    cp_nhan_cong_truc_tiep: float = 20000000.0
    cp_san_xuat_chung: float = 12000000.0
    d_cuoi_ky: float = 11000000.0
    sl_hoan_thanh: float = 1000.0
    phe_lieu_thu_hoi: float = 1000000.0
    regime: str = "TT99"
    # Thuộc tính kiểm soát công suất bình thường VAS 02
    cong_suat_thuc_te: Optional[float] = None
    cong_suat_dinh_muc: Optional[float] = None
    ty_le_sxc_co_dinh: Optional[float] = 50.0


@app.post("/api/cost/calculate")
def api_calculate_cost(req: ProductCostRequest):
    try:
        # Nếu áp dụng VAS 02 công suất bình thường
        cp_sxc_hop_ly = req.cp_san_xuat_chung
        sxc_duoi_cong_suat = 0.0
        vas02_applied = False

        if req.cong_suat_thuc_te and req.cong_suat_dinh_muc and req.cong_suat_dinh_muc > 0:
            if req.cong_suat_thuc_te < req.cong_suat_dinh_muc:
                vas02_applied = True
                ty_le_co_dinh = (req.ty_le_sxc_co_dinh or 50.0) / 100.0
                sxc_co_dinh = req.cp_san_xuat_chung * ty_le_co_dinh
                sxc_bien_doi = req.cp_san_xuat_chung - sxc_co_dinh
                he_so = req.cong_suat_thuc_te / req.cong_suat_dinh_muc
                sxc_co_dinh_hop_ly = sxc_co_dinh * he_so
                sxc_duoi_cong_suat = sxc_co_dinh - sxc_co_dinh_hop_ly
                cp_sxc_hop_ly = sxc_bien_doi + sxc_co_dinh_hop_ly

        res = calculate_product_cost(
            product_name=req.product_name,
            d_dau_ky=req.d_dau_ky,
            cp_nvl_truc_tiep=req.cp_nvl_truc_tiep,
            cp_nhan_cong_truc_tiep=req.cp_nhan_cong_truc_tiep,
            cp_san_xuat_chung=cp_sxc_hop_ly,
            d_cuoi_ky=req.d_cuoi_ky,
            sl_hoan_thanh=req.sl_hoan_thanh,
            phe_lieu_thu_hoi=req.phe_lieu_thu_hoi,
            regime=req.regime,
        )

        res["vas02_info"] = {
            "applied": vas02_applied,
            "cong_suat_thuc_te": req.cong_suat_thuc_te,
            "cong_suat_dinh_muc": req.cong_suat_dinh_muc,
            "sxc_duoi_cong_suat_tinh_vao_632": round(sxc_duoi_cong_suat, 2),
            "sxc_hop_ly_tinh_vao_154": round(cp_sxc_hop_ly, 2),
        }

        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class OverheadAllocateRequest(BaseModel):
    total_overhead: float
    criteria: str = "nvl"
    products: List[Dict[str, Any]]


@app.post("/api/cost/allocate")
def api_allocate_overhead(req: OverheadAllocateRequest):
    try:
        res = allocate_overhead_costs(
            total_overhead=req.total_overhead,
            products=req.products,
            criteria=req.criteria,
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class ExportCostSheetRequest(BaseModel):
    product_name: str
    ky_tinh_gia_thanh: str = "Tháng 10/2026"
    sl_hoan_thanh: float
    d_dau_ky_dict: Dict[str, float]
    phat_sinh_dict: Dict[str, float]
    d_cuoi_ky_dict: Dict[str, float]


@app.post("/api/cost/export-excel")
def api_export_cost_excel(req: ExportCostSheetRequest):
    tmp_out = os.path.join(tempfile.gettempdir(), f"The_Tinh_Gia_Thanh_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    try:
        export_cost_sheet_excel(
            output_excel_path=tmp_out,
            product_name=req.product_name,
            ky_tinh_gia_thanh=req.ky_tinh_gia_thanh,
            sl_hoan_thanh=req.sl_hoan_thanh,
            d_dau_ky_dict=req.d_dau_ky_dict,
            phat_sinh_dict=req.phat_sinh_dict,
            d_cuoi_ky_dict=req.d_cuoi_ky_dict,
        )
        return FileResponse(
            tmp_out,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=f"The_Tinh_Gia_Thanh_{req.product_name}.xlsx",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# 5. API SỔ NHẬT KÝ CHUNG & CƠ SỞ DỮ LIỆU
# ==========================================
class JournalEntryInput(BaseModel):
    ngay_ghi_so: str
    so_chung_tu: str
    ngay_chung_tu: str
    dien_giai: str
    tk_no: str
    tk_co: str
    so_tien: float


@app.get("/api/journal/entries")
def get_journal_entries(
    search: Optional[str] = None,
    tk: Optional[str] = None,
    fromDate: Optional[str] = None,
    toDate: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    conn = get_db_connection()
    cur = conn.cursor()

    sql = "SELECT * FROM nhat_ky_chung WHERE 1=1"
    params = []

    if search:
        sql += " AND (so_chung_tu LIKE ? OR dien_giai LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    if tk:
        sql += " AND (tk_no LIKE ? OR tk_co LIKE ?)"
        params.extend([f"{tk}%", f"{tk}%"])
    if fromDate:
        sql += " AND ngay_ghi_so >= ?"
        params.append(fromDate)
    if toDate:
        sql += " AND ngay_ghi_so <= ?"
        params.append(toDate)

    # Đếm tổng
    count_sql = f"SELECT COUNT(*), COALESCE(SUM(so_tien), 0) FROM ({sql})"
    cur.execute(count_sql, params)
    count_row = cur.fetchone()
    total_records = count_row[0] if count_row else 0
    total_amount = count_row[1] if count_row else 0.0

    sql += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cur.execute(sql, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    return {
        "total_records": total_records,
        "total_amount": total_amount,
        "items": rows,
    }


@app.post("/api/journal/entries")
def create_journal_entry(entry: JournalEntryInput):
    if entry.so_tien <= 0:
        raise HTTPException(status_code=400, detail="Số tiền phát sinh phải lớn hơn 0")
    if entry.tk_no == entry.tk_co:
        raise HTTPException(status_code=400, detail="Tài khoản Nợ và Tài khoản Có không được trùng nhau")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO nhat_ky_chung (ngay_ghi_so, so_chung_tu, ngay_chung_tu, dien_giai, tk_no, tk_co, so_tien)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        entry.ngay_ghi_so,
        entry.so_chung_tu,
        entry.ngay_chung_tu,
        entry.dien_giai,
        entry.tk_no,
        entry.tk_co,
        entry.so_tien,
    ))
    new_id = cur.lastrowid
    conn.commit()
    conn.close()

    return {
        "status": "success",
        "id": new_id,
        "message": f"Đã ghi sổ thành công bút toán {entry.so_chung_tu}",
    }


@app.get("/api/journal/stats")
def get_journal_stats():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*), COALESCE(SUM(so_tien), 0) FROM nhat_ky_chung")
    r = cur.fetchone()
    total_txns = r[0] if r else 0
    total_amt = r[1] if r else 0.0

    cur.execute("""
        SELECT tk_no, SUM(so_tien) as total 
        FROM nhat_ky_chung 
        GROUP BY tk_no 
        ORDER BY total DESC LIMIT 5
    """)
    top_debit = [dict(x) for x in cur.fetchall()]

    cur.execute("""
        SELECT tk_co, SUM(so_tien) as total 
        FROM nhat_ky_chung 
        GROUP BY tk_co 
        ORDER BY total DESC LIMIT 5
    """)
    top_credit = [dict(x) for x in cur.fetchall()]

    conn.close()
    return {
        "total_transactions": total_txns,
        "total_amount": total_amt,
        "top_debit_accounts": top_debit,
        "top_credit_accounts": top_credit,
    }


@app.get("/api/journal/export-excel")
def export_journal_excel_api():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT ngay_ghi_so, so_chung_tu, ngay_chung_tu, dien_giai, tk_no, tk_co, so_tien FROM nhat_ky_chung ORDER BY id ASC")
    rows = cur.fetchall()
    conn.close()

    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Nhat_Ky_Chung"

    ws["A1"] = "HỆ THỐNG TRỢ LÝ KẾ TOÁN AI DOANH NGHIỆP VIỆT NAM"
    ws["A1"].font = Font(name="Times New Roman", size=11, bold=True)
    ws["A4"] = "SỔ NHẬT KÝ CHUNG"
    ws["A4"].font = Font(name="Times New Roman", size=16, bold=True, color="002060")
    ws["A4"].alignment = Alignment(horizontal="center")
    ws.merge_cells("A4:G4")
    ws["A5"] = f"Mẫu S03a-DN (Trích xuất ngày {datetime.now().strftime('%d/%m/%Y')})"
    ws["A5"].alignment = Alignment(horizontal="center")
    ws.merge_cells("A5:G5")

    headers = ["Ngày ghi sổ", "Số hiệu CT", "Ngày CT", "Diễn giải", "TK Nợ", "TK Có", "Số tiền (VND)"]
    header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    header_font = Font(name="Times New Roman", size=11, bold=True, color="FFFFFF")

    for col_num, h in enumerate(headers, 1):
        cell = ws.cell(row=7, column=col_num)
        cell.value = h
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )

    for r_idx, r in enumerate(rows, start=8):
        vals = [r[0], r[1], r[2], r[3], r[4], r[5], r[6]]
        for c_idx, val in enumerate(vals, start=1):
            cell = ws.cell(row=r_idx, column=c_idx)
            cell.value = val
            cell.font = Font(name="Times New Roman", size=11)
            cell.border = thin_border
            if c_idx in [1, 2, 3, 5, 6]:
                cell.alignment = Alignment(horizontal="center")
            elif c_idx == 7:
                cell.number_format = '#,##0'
                cell.alignment = Alignment(horizontal="right")

    tot_idx = 8 + len(rows)
    ws.cell(row=tot_idx, column=4, value="CỘNG PHÁT SINH").font = Font(name="Times New Roman", size=11, bold=True)
    sum_cell = ws.cell(row=tot_idx, column=7)
    sum_cell.value = f"=SUM(G8:G{tot_idx-1})"
    sum_cell.font = Font(name="Times New Roman", size=11, bold=True, color="C00000")
    sum_cell.number_format = '#,##0'
    sum_cell.alignment = Alignment(horizontal="right")

    col_widths = [15, 15, 15, 45, 12, 12, 20]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

    tmp_file = os.path.join(tempfile.gettempdir(), f"So_Nhat_Ky_Chung_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    wb.save(tmp_file)

    return FileResponse(
        tmp_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="So_Nhat_Ky_Chung_S03a.xlsx"
    )


# ==========================================
# 6. API SỔ CÁI BEANCOUNT
# ==========================================
@app.get("/api/beancount/verify")
def verify_beancount():
    if not os.path.exists(BEANCOUNT_PATH):
        raise HTTPException(status_code=404, detail="Không tìm thấy file Sổ cái Beancount")
    try:
        res = verify_beancount_ledger(BEANCOUNT_PATH)
        with open(BEANCOUNT_PATH, "r", encoding="utf-8") as f:
            raw_text = f.read()
        res["raw_content"] = raw_text
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# 7. API ĐỐI SOÁT SAO KÊ NGÂN HÀNG (TK 112)
# ==========================================
def run_bank_reconciliation(file_path: str):
    import pandas as pd
    try:
        df = pd.read_excel(file_path, header=None)
    except Exception as e:
        raise ValueError(f"Không thể đọc file sao kê Excel: {str(e)}")

    # Tìm hàng tiêu đề chứa STT, Ngày, Nợ, Có
    header_idx = 12
    for idx, row in df.iterrows():
        row_str = " ".join([str(c) for c in row.values if pd.notna(c)]).lower()
        if "stt" in row_str and ("nợ" in row_str or "ghi nợ" in row_str or "debit" in row_str or "ngày" in row_str):
            header_idx = idx
            break

    df_txns = pd.read_excel(file_path, skiprows=header_idx + 1)
    bank_txns = []

    for _, row in df_txns.iterrows():
        try:
            val_0 = row.iloc[0]
            if pd.isna(val_0):
                continue
            stt = int(val_0)
            ngay = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
            debit = float(str(row.iloc[3]).replace(",", "")) if pd.notna(row.iloc[3]) and str(row.iloc[3]).strip() else 0.0
            credit = float(str(row.iloc[4]).replace(",", "")) if pd.notna(row.iloc[4]) and str(row.iloc[4]).strip() else 0.0
            balance = float(str(row.iloc[5]).replace(",", "")) if pd.notna(row.iloc[5]) and str(row.iloc[5]).strip() else 0.0
            content = str(row.iloc[6]).strip() if len(row) > 6 and pd.notna(row.iloc[6]) else ""

            bank_txns.append({
                "stt": stt,
                "ngay": ngay,
                "ghi_no_tien_ra": debit,
                "ghi_co_tien_vao": credit,
                "so_du": balance,
                "noi_dung": content,
            })
        except Exception:
            continue

    # Lấy các bút toán TK 112 từ SQLite
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, ngay_ghi_so, so_chung_tu, dien_giai, tk_no, tk_co, so_tien 
        FROM nhat_ky_chung 
        WHERE tk_no LIKE '112%' OR tk_co LIKE '112%'
    """)
    ledger_rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    for l in ledger_rows:
        l["matched"] = False

    reconciled_list = []
    matched_count = 0
    total_bank_in = 0.0
    total_bank_out = 0.0

    for b in bank_txns:
        total_bank_in += b["ghi_co_tien_vao"]
        total_bank_out += b["ghi_no_tien_ra"]

        amt = b["ghi_no_tien_ra"] if b["ghi_no_tien_ra"] > 0 else b["ghi_co_tien_vao"]
        matched_ledger = None

        for l in ledger_rows:
            if not l["matched"] and abs(l["so_tien"] - amt) < 1.0:
                l["matched"] = True
                matched_ledger = l
                matched_count += 1
                break

        reconciled_list.append({
            **b,
            "status": "MATCHED" if matched_ledger else "BANK_ONLY",
            "matched_info": matched_ledger,
        })

    unmatched_ledger = [l for l in ledger_rows if not l["matched"]]

    return {
        "file_analyzed": os.path.basename(file_path),
        "total_bank_transactions": len(bank_txns),
        "matched_count": matched_count,
        "bank_only_count": len(bank_txns) - matched_count,
        "ledger_only_count": len(unmatched_ledger),
        "total_bank_in": total_bank_in,
        "total_bank_out": total_bank_out,
        "transactions": reconciled_list,
        "unmatched_ledger_transactions": unmatched_ledger,
    }


@app.post("/api/reconcile")
async def reconcile_api(file: Optional[UploadFile] = File(None), use_sample: bool = Form(False)):
    if use_sample:
        if not os.path.exists(SAMPLE_BANK_FILE):
            raise HTTPException(status_code=404, detail="Không tìm thấy file sao kê mẫu Vietcombank")
        res = run_bank_reconciliation(SAMPLE_BANK_FILE)
        return res

    if not file:
        raise HTTPException(status_code=400, detail="Vui lòng tải lên file sao kê Excel hoặc chọn dùng file mẫu")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xls") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        res = run_bank_reconciliation(tmp_path)
        return res
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# ==========================================
# 8. API CƠ SỞ PHÁP LÝ & MA TRẬN QUY PHẠM
# ==========================================
@app.get("/api/legal-basis")
def get_legal_basis():
    legal_path = os.path.join(BASE_DIR, "legal-basis.md")
    content = ""
    if os.path.exists(legal_path):
        with open(legal_path, "r", encoding="utf-8") as f:
            content = f.read()

    return {
        "title": "Cơ Sở Pháp Lý & Ma Trận Hiệu Lực Kế Toán - Thuế Việt Nam",
        "last_updated": "2026-10-17",
        "pillars": [
            {
                "category": "Chế độ Kế toán Doanh nghiệp",
                "criterion": "Xác định theo Năm tài chính",
                "rules": [
                    {"code": "TT 99/2025/TT-BTC", "target": "Năm tài chính từ 01/01/2026 (Thay thế TT 200)", "status": "Hiệu lực mới"},
                    {"code": "TT 200/2014/TT-BTC", "target": "Năm tài chính bắt đầu trước 01/01/2026", "status": "Kỳ cũ"},
                    {"code": "TT 133/2016/TT-BTC", "target": "Doanh nghiệp nhỏ và vừa (DNNVV)", "status": "Đang áp dụng"},
                    {"code": "TT 58/2026/TT-BTC", "target": "Doanh nghiệp siêu nhỏ (Từ 01/07/2026)", "status": "Sắp hiệu lực"},
                ]
            },
            {
                "category": "Hóa đơn & Chứng từ",
                "criterion": "Xác định theo Ngày lập hóa đơn",
                "rules": [
                    {"code": "NĐ 254/2026/NĐ-CP & TT 91/2026/TT-BTC", "target": "Hóa đơn lập từ 01/07/2026 trở đi", "status": "Mới nhất"},
                    {"code": "NĐ 123/2020 & TT 32/2025 (sửa NĐ 70/2025)", "target": "Hóa đơn lập từ 01/06/2025 đến 30/06/2026", "status": "Chuyển tiếp"},
                    {"code": "NĐ 123/2020 & TT 78/2021", "target": "Hóa đơn lập trước 01/06/2025", "status": "Kỳ cũ"},
                ]
            },
            {
                "category": "Thuế TNDN & Thuế TNCN",
                "criterion": "Xác định theo Kỳ tính thuế",
                "rules": [
                    {"code": "Luật Thuế TNDN số 67/2025/QH15", "target": "Kỳ tính thuế từ năm 2025 trở đi", "status": "Hiệu lực"},
                    {"code": "Luật Thuế TNCN số 109/2025/QH15 & TT 87/2026", "target": "Kỳ tính thuế từ 2026 (Từ 01/07/2026 toàn diện)", "status": "Hiệu lực"},
                ]
            },
            {
                "category": "Thuế GTGT & Quản lý thuế",
                "criterion": "Xác định theo Thời điểm phát sinh / Ngày nộp",
                "rules": [
                    {"code": "Luật Thuế GTGT số 48/2024/QH15", "target": "Hiệu lực từ 01/07/2025", "status": "Hiệu lực"},
                    {"code": "Luật Quản lý thuế số 108/2025/QH15", "target": "Hiệu lực từ 01/07/2026", "status": "Hiệu lực"},
                ]
            }
        ],
        "markdown_full": content
    }


# ==========================================
# 8b. HÓA ĐƠN NGÂN HÀNG VIETCOMBANK & HẠCH TOÁN
# ==========================================
BANK_INVOICES_DIR = os.path.join(BASE_DIR, "data", "chung_tu", "hoa_don_bank")


@app.get("/api/bank-invoices/months")
def get_bank_invoice_months():
    """Lấy danh sách các tháng có dữ liệu hóa đơn ngân hàng."""
    if not os.path.exists(BANK_INVOICES_DIR):
        return {"months": []}
    dirs = [d for d in os.listdir(BANK_INVOICES_DIR) if os.path.isdir(os.path.join(BANK_INVOICES_DIR, d)) and re.match(r"^\d{4}-\d{2}$", d)]
    dirs.sort(reverse=True)
    return {"months": dirs}


@app.get("/api/bank-invoices/list")
def get_bank_invoices(month: Optional[str] = None):
    """
    Lấy danh sách chi tiết hóa đơn ngân hàng theo tháng.
    """
    if not os.path.exists(BANK_INVOICES_DIR):
        return {"month": month, "invoices": [], "summary": {}}

    available_months = [d for d in os.listdir(BANK_INVOICES_DIR) if os.path.isdir(os.path.join(BANK_INVOICES_DIR, d)) and re.match(r"^\d{4}-\d{2}$", d)]
    available_months.sort(reverse=True)
    if not month and available_months:
        month = available_months[0]
    elif not month:
        return {"month": "", "invoices": [], "summary": {}}

    month_dir = os.path.join(BANK_INVOICES_DIR, month)
    if not os.path.exists(month_dir):
        return {
            "month": month,
            "available_months": available_months,
            "summary": {
                "total_invoices": 0,
                "total_amount": 0,
                "total_vat": 0,
                "total_payment": 0,
                "total_interest": 0,
                "total_fees": 0
            },
            "has_excel": False,
            "excel_filename": "",
            "invoices": []
        }

    excel_files = glob.glob(os.path.join(month_dir, "*.xlsx"))
    invoices = []
    
    if excel_files:
        try:
            import pandas as pd
            df = pd.read_excel(excel_files[0])
            df = df.fillna("")
            records = df.to_dict(orient="records")
            for r in records:
                pdf_name = str(r.get("Tên File PDF", ""))
                xml_name = str(r.get("Tên File XML", ""))
                has_pdf = os.path.exists(os.path.join(month_dir, pdf_name)) if pdf_name else False
                has_xml = os.path.exists(os.path.join(month_dir, xml_name)) if xml_name else False
                
                invoices.append({
                    "stt": r.get("STT"),
                    "so_hd": str(r.get("Số Hóa Đơn", "")),
                    "ngay_hd": str(r.get("Ngày Hóa Đơn", "")),
                    "ngay_ky": str(r.get("Ngày Ký", "")),
                    "ky_hieu": str(r.get("Ký Hiệu", "")),
                    "nha_cung_cap": str(r.get("Nhà Cung Cấp", "Ngân hàng TMCP Ngoại thương Việt Nam (VCB)")),
                    "mst": str(r.get("MST Bên Bán", "")),
                    "ghi_chu": str(r.get("Nội Dung / Ghi Chú", "")),
                    "thanh_tien": float(r.get("Thành Tiền (VND)", 0) or 0),
                    "thue_suat": str(r.get("Thuế Suất", "")),
                    "tien_thue": float(r.get("Tiền Thuế (VND)", 0) or 0),
                    "tong_tien": float(r.get("Tổng Thanh Toán (VND)", 0) or 0),
                    "tk_no": str(r.get("TK Nợ", "")),
                    "tk_co": str(r.get("TK Có", "1121")),
                    "tk_thue": str(r.get("TK Thuế", "")),
                    "pdf_file": pdf_name,
                    "xml_file": xml_name,
                    "has_pdf": has_pdf,
                    "has_xml": has_xml
                })
        except Exception as e:
            print(f"Error reading Excel {excel_files[0]}: {e}")

    # Fallback: scan PDF/XML files directly in directory if excel was missing or empty
    if not invoices:
        pdf_files = sorted(glob.glob(os.path.join(month_dir, "*.pdf")))
        for idx, p_path in enumerate(pdf_files, 1):
            fname = os.path.basename(p_path)
            base_no_ext = os.path.splitext(fname)[0]
            xml_name = f"{base_no_ext}.xml"
            has_xml = os.path.exists(os.path.join(month_dir, xml_name))
            
            parts = base_no_ext.split("-", 2)
            ngay_str = parts[0] if len(parts) > 0 else ""
            so_str = parts[1] if len(parts) > 1 else ""
            remarks_str = parts[2] if len(parts) > 2 else base_no_ext
            
            ngay_formatted = ""
            if len(ngay_str) == 8 and ngay_str.isdigit():
                ngay_formatted = f"{ngay_str[:2]}/{ngay_str[2:4]}/{ngay_str[4:]}"
                
            invoices.append({
                "stt": idx,
                "so_hd": so_str,
                "ngay_hd": ngay_formatted,
                "ngay_ky": ngay_formatted,
                "ky_hieu": "",
                "nha_cung_cap": "Ngân hàng TMCP Ngoại thương Việt Nam (VCB)",
                "mst": "0100112437-016",
                "ghi_chu": remarks_str,
                "thanh_tien": 0.0,
                "thue_suat": "",
                "tien_thue": 0.0,
                "tong_tien": 0.0,
                "tk_no": "635" if any(k in remarks_str.lower() for k in ["lai vay", "lãi vay", "thu lai"]) else "6422",
                "tk_co": "1121",
                "tk_thue": "",
                "pdf_file": fname,
                "xml_file": xml_name if has_xml else "",
                "has_pdf": True,
                "has_xml": has_xml
            })

    total_invoices = len(invoices)
    total_amount = sum(inv["thanh_tien"] for inv in invoices)
    total_vat = sum(inv["tien_thue"] for inv in invoices)
    total_payment = sum(inv["tong_tien"] for inv in invoices)
    total_interest = sum(inv["tong_tien"] for inv in invoices if str(inv["tk_no"]) == "635")
    total_fees = sum(inv["thanh_tien"] for inv in invoices if str(inv["tk_no"]) == "6422")

    return {
        "month": month,
        "available_months": available_months,
        "summary": {
            "total_invoices": total_invoices,
            "total_amount": total_amount,
            "total_vat": total_vat,
            "total_payment": total_payment,
            "total_interest": total_interest,
            "total_fees": total_fees
        },
        "has_excel": len(excel_files) > 0,
        "excel_filename": os.path.basename(excel_files[0]) if excel_files else "",
        "invoices": invoices
    }


# State store for background VCB download task
download_state: Dict[str, Any] = {
    "is_running": False,
    "month": "",
    "status": "idle",
    "progress": 0,
    "total": 0,
    "current": 0,
    "message": "",
    "logs": [],
    "error": None,
    "started_at": None,
    "completed_at": None
}

download_lock = threading.Lock()


def download_worker(month_str: str, account: str, fee_only: bool, force: bool):
    global download_state

    def on_progress(p: dict):
        with download_lock:
            status = p.get("status", "running")
            download_state["status"] = status
            download_state["message"] = p.get("message", "")
            if "total" in p:
                download_state["total"] = p["total"]
            if "current" in p:
                download_state["current"] = p["current"]
                if download_state["total"] > 0:
                    download_state["progress"] = int((p["current"] / download_state["total"]) * 100)
            log_entry = {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "message": p.get("message", "")
            }
            download_state["logs"].append(log_entry)
            if len(download_state["logs"]) > 50:
                download_state["logs"].pop(0)

    try:
        from tools.download_month_invoices import run_direct_api
        results = run_direct_api(
            month_str=month_str,
            account=account,
            fee_only=fee_only,
            force=force,
            sync_db=True,
            progress_callback=on_progress
        )
        with download_lock:
            download_state["is_running"] = False
            download_state["status"] = "completed"
            download_state["progress"] = 100
            download_state["completed_at"] = datetime.now().isoformat()
            download_state["message"] = f"Đã tải thành công {len(results)} hóa đơn từ Vietcombank!"
            download_state["logs"].append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "message": f"HOÀN THÀNH: Đã lưu {len(results)} hóa đơn (PDF & XML)!"
            })
    except Exception as e:
        with download_lock:
            download_state["is_running"] = False
            download_state["status"] = "error"
            download_state["error"] = str(e)
            download_state["message"] = f"Lỗi tải từ Vietcombank: {str(e)}"
            download_state["logs"].append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "message": f"LỖI: {str(e)}"
            })


class DownloadVCBInvoicesRequest(BaseModel):
    month: str = Field(..., description="Tháng cần tải (ví dụ: '10/2026' hoặc '2026-10')")
    account: Optional[str] = Field("", description="Số tài khoản ngân hàng (tùy chọn)")
    fee_only: Optional[bool] = Field(False, description="Chỉ tải phí dịch vụ")
    force: Optional[bool] = Field(False, description="Ghi đè file nếu đã tồn tại")


@app.post("/api/bank-invoices/download")
def api_download_bank_invoices(req: DownloadVCBInvoicesRequest):
    """Khởi chạy tiến trình tải hóa đơn (PDF & XML) từ Vietcombank qua Direct REST API trong nền."""
    global download_state
    
    with download_lock:
        if download_state["is_running"]:
            return {
                "success": False,
                "is_running": True,
                "message": f"Tiến trình tải hóa đơn tháng {download_state['month']} đang chạy!"
            }
        
        m_str = req.month.strip()
        if "-" in m_str:
            parts = m_str.split("-")
            if len(parts) == 2:
                m_str = f"{parts[1]}/{parts[0]}"
                
        download_state["is_running"] = True
        download_state["month"] = m_str
        download_state["status"] = "starting"
        download_state["progress"] = 0
        download_state["total"] = 0
        download_state["current"] = 0
        download_state["message"] = f"Khởi tạo tiến trình tải kỳ {m_str}..."
        download_state["logs"] = [{
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "message": f"Khởi tạo tiến trình tải hóa đơn kỳ {m_str}..."
        }]
        download_state["error"] = None
        download_state["started_at"] = datetime.now().isoformat()
        download_state["completed_at"] = None

    t = threading.Thread(
        target=download_worker,
        args=(m_str, req.account or "", req.fee_only or False, req.force or False),
        daemon=True
    )
    t.start()

    return {
        "success": True,
        "is_running": True,
        "month": m_str,
        "message": f"Đã bắt đầu tải hóa đơn tháng {m_str} từ Vietcombank trong nền."
    }


@app.get("/api/bank-invoices/download-status")
def get_download_status():
    """Lấy trạng thái và nhật ký tiến trình tải hóa đơn Vietcombank theo thời gian thực."""
    with download_lock:
        return download_state.copy()


@app.post("/api/bank-invoices/sync-to-journal")
def sync_bank_invoices_to_journal(month: str = Query(...)):
    """
    Đồng bộ toàn bộ hóa đơn ngân hàng của tháng vào Sổ Nhật Ký Chung trong SQLite DB.
    """
    month_dir = os.path.join(BANK_INVOICES_DIR, month)
    if not os.path.exists(month_dir):
        raise HTTPException(status_code=404, detail="Không tìm thấy dữ liệu tháng yêu cầu")

    excel_files = glob.glob(os.path.join(month_dir, "*.xlsx"))
    if not excel_files:
        raise HTTPException(status_code=404, detail="Không tìm thấy file Bảng kê Excel của tháng")

    import pandas as pd
    df = pd.read_excel(excel_files[0])
    df = df.fillna("")
    records = df.to_dict(orient="records")

    conn = get_db_connection()
    cur = conn.cursor()
    added_count = 0

    for r in records:
        so_no = str(r.get("Số Hóa Đơn", ""))
        so_hd = f"HD{so_no.zfill(8)}"
        ngay_hd_raw = str(r.get("Ngày Hóa Đơn", ""))
        try:
            d, m, y = ngay_hd_raw.split("/")
            ngay_hd = f"{y}-{m}-{d}"
        except Exception:
            ngay_hd = ngay_hd_raw or f"{month}-01"

        remarks = str(r.get("Nội Dung / Ghi Chú", ""))
        amount = float(r.get("Thành Tiền (VND)", 0) or 0)
        vat = float(r.get("Tiền Thuế (VND)", 0) or 0)
        total = float(r.get("Tổng Thanh Toán (VND)", 0) or 0)
        is_loan = any(k in remarks.lower() for k in ['lai vay', 'lãi vay', 'tai khoan vay', 'khoan vay'])

        entries = []
        if is_loan:
            entries.append((ngay_hd, so_hd, ngay_hd, f"Chi phí lãi tiền vay VCB - {remarks}", '635', '1121', total or amount))
        else:
            cost_amount = amount if amount > 0 else (total - vat)
            entries.append((ngay_hd, so_hd, ngay_hd, f"Phí dịch vụ ngân hàng VCB - {remarks}", '6422', '1121', cost_amount))
            if vat > 0:
                entries.append((ngay_hd, so_hd, ngay_hd, f"Thuế GTGT đầu vào phí DV NH VCB ({so_hd})", '1331', '1121', vat))

        for entry in entries:
            cur.execute("SELECT id FROM nhat_ky_chung WHERE so_chung_tu = ? AND tk_no = ?", (entry[1], entry[4]))
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO nhat_ky_chung (ngay_ghi_so, so_chung_tu, ngay_chung_tu, dien_giai, tk_no, tk_co, so_tien)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, entry)
                added_count += 1

    conn.commit()
    conn.close()

    return {
        "success": True,
        "added_count": added_count,
        "month": month,
        "message": f"Đã đồng bộ thành công {added_count} bút toán vào Sổ Nhật Ký Chung"
    }


@app.get("/api/bank-invoices/export-misa-excel")
def export_bank_invoices_excel(month: str = Query(...)):
    """Tải file Bảng kê hóa đơn ngân hàng định dạng chuẩn MISA."""
    month_dir = os.path.join(BANK_INVOICES_DIR, month)
    if not os.path.exists(month_dir):
        raise HTTPException(status_code=404, detail="Không tìm thấy dữ liệu tháng yêu cầu")

    excel_files = glob.glob(os.path.join(month_dir, "*.xlsx"))
    if not excel_files:
        raise HTTPException(status_code=404, detail="Không tìm thấy file Excel bảng kê")

    return FileResponse(
        excel_files[0],
        filename=os.path.basename(excel_files[0]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.get("/api/bank-invoices/file")
def get_bank_invoice_file(month: str = Query(...), filename: str = Query(...)):
    """Tải hoặc xem trước file PDF / XML của hóa đơn ngân hàng."""
    month_dir = os.path.join(BANK_INVOICES_DIR, month)
    file_path = os.path.join(month_dir, filename)
    
    if not os.path.abspath(file_path).startswith(os.path.abspath(month_dir)):
        raise HTTPException(status_code=403, detail="Yêu cầu không hợp lệ")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File không tồn tại trên hệ thống")

    media_type = "application/pdf" if filename.lower().endswith(".pdf") else "application/xml"
    return FileResponse(file_path, filename=filename, media_type=media_type)


@app.get("/api/bank-invoices/download-zip")
def download_bank_invoices_zip(month: Optional[str] = Query(None)):
    """Tải toàn bộ chứng từ (PDF & XML) dạng file nén ZIP cho một kỳ hoặc tất cả các kỳ."""
    if not os.path.exists(BANK_INVOICES_DIR):
        raise HTTPException(status_code=404, detail="Chưa có dữ liệu hóa đơn ngân hàng trên hệ thống")

    zip_buffer = io.BytesIO()

    # Xử lý chuẩn hóa tên tháng nếu người dùng truyền dạng MM/YYYY
    target_month = month.strip() if month else None
    if target_month and "/" in target_month:
        parts = target_month.split("/")
        if len(parts) == 2:
            target_month = f"{parts[1]}-{parts[0].zfill(2)}"

    if target_month and target_month != "all":
        month_dir = os.path.join(BANK_INVOICES_DIR, target_month)
        if not os.path.exists(month_dir):
            raise HTTPException(status_code=404, detail=f"Không tìm thấy thư mục chứng từ cho kỳ {target_month}")

        files = [f for f in os.listdir(month_dir) if f.lower().endswith(('.pdf', '.xml', '.xlsx'))]
        if not files:
            raise HTTPException(status_code=404, detail=f"Kỳ {target_month} chưa có file chứng từ PDF hoặc XML nào")

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for fname in files:
                fpath = os.path.join(month_dir, fname)
                zf.write(fpath, arcname=fname)

        zip_buffer.seek(0)
        zip_filename = f"Chung_Tu_Bank_{target_month}.zip"
    else:
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            count = 0
            for root, dirs, files in os.walk(BANK_INVOICES_DIR):
                for fname in files:
                    if fname.lower().endswith(('.pdf', '.xml', '.xlsx')):
                        fpath = os.path.join(root, fname)
                        rel_path = os.path.relpath(fpath, BANK_INVOICES_DIR)
                        zf.write(fpath, arcname=rel_path)
                        count += 1
            if count == 0:
                raise HTTPException(status_code=404, detail="Chưa có file chứng từ nào trên hệ thống")

        zip_buffer.seek(0)
        zip_filename = f"Toan_Bo_Chung_Tu_Bank_{datetime.now().strftime('%Y%m%d')}.zip"

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{zip_filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )


# ==========================================
# 9. MOUNT FRONTEND STATIC ASSETS
# ==========================================
FRONTEND_DIST = os.path.join(BASE_DIR, "web", "frontend", "dist")

if os.path.exists(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
else:
    @app.get("/")
    def index_fallback():
        return {
            "message": "Vietnam Accounting Suite API Server is running",
            "api_docs": "/docs",
            "frontend_status": "Vui lòng build frontend tại web/frontend (npm run build) hoặc chạy npm run dev trên cổng 3000",
        }
