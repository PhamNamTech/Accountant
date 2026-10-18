"""
HỆ THỐNG TỰ ĐỘNG HÓA HÓA ĐƠN ĐIỆN TỬ VIETCOMBANK (VCB) QUA DIRECT REST API
=============================================================================
Kiến trúc tối ưu:
1. Giao tiếp trực tiếp với Backend REST API của Vietcombank:
   - Login Endpoint: /api/system/account/login-portal
   - Query Endpoint: /api/portal/PortalApiService/portal-private
   - Download XML:   /api/portal/PortalApiService/download/private/xml
   - Download PDF:   /api/portal/PortalApiService/download/private/unofficial
2. Giải mã cơ chế bảo mật của Vietcombank:
   - Thuật toán mã hóa: AES-128-CBC với PKCS7 Padding
   - Khóa mật mã (Key & IV): b"8080808080808080"
   - Định danh xác thực: Bearer Token JWT (Chuẩn ABP Framework)
3. Vượt qua Web Application Firewall (WAF/Cloudflare) của Ngân hàng:
   - Sử dụng phiên Chromium ngầm để bảo đảm Fingerprint TLS (JA3/JA4) hợp lệ 100%.
   - Không phụ thuộc vào giao diện DOM, nút bấm hay đóng mở Drawer.
   - Tốc độ xử lý: ~3 - 5 giây cho toàn bộ hóa đơn của cả tháng!
4. Đọc trực tiếp nội dung PDF để trích xuất:
   - Ngày ký (Signing Date) -> DDMMYYYY
   - Số hóa đơn (Invoice No) -> 8 chữ số
   - Ghi chú (Remarks) -> Chuẩn hóa tên file, loại bỏ ký tự cấm
5. Tự động hạch toán (ketoan.db) và xuất Bảng kê Excel chuẩn MISA.
"""

import sys
import os
import time
import argparse
import json
import base64
import io
import re
import calendar
import sqlite3
from datetime import datetime
import pypdf
import pandas as pd
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# Tự động nạp biến môi trường từ .env
load_dotenv()

sys.stdout.reconfigure(encoding='utf-8')

# Cấu hình tài khoản & Mật mã (bảo mật qua biến môi trường / .env)
DEFAULT_USERNAME = os.environ.get("VCB_USERNAME", "")
DEFAULT_PASSWORD = os.environ.get("VCB_PASSWORD", "")
AES_KEY = b"8080808080808080"
AES_IV = b"8080808080808080"
BASE_BANK_DIR = r"F:\Accountant\data\chung_tu\hoa_don_bank"
DEFAULT_DB_PATH = r"F:\Accountant\data\database\ketoan.db"

def aes_encrypt(obj):
    """Mã hóa payload JSON theo chuẩn AES-128-CBC của cổng Vietcombank."""
    data_str = json.dumps(obj, separators=(',', ':'), ensure_ascii=False)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data_str.encode('utf-8')) + padder.finalize()
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(AES_IV))
    encryptor = cipher.encryptor()
    cipher_bytes = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(cipher_bytes).decode('utf-8')

def parse_pdf_metadata(pdf_bytes):
    """Trích xuất Ngày ký, Số HĐ, Ghi chú nghiệp vụ và Số tiền từ PDF."""
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    full_text = '\n'.join([p.extract_text() for p in reader.pages])

    # 1. Ngày ký
    match_ngay_ky = re.search(r'Ngày ký\s*:\s*(?:\n\s*)*(\d{2}/\d{2}/\d{4})', full_text)
    if not match_ngay_ky:
        match_ngay_ky = re.search(r'(\d{2}/\d{2}/\d{4})', full_text)
    ngay_ky_raw = match_ngay_ky.group(1) if match_ngay_ky else ""
    ngay_ky_clean = ngay_ky_raw.replace('/', '')

    # 2. Số hóa đơn (No)
    match_so = re.search(r'Số\s*(?:\n\s*)?\(No\)\s*(?:\n\s*)?:?\s*(?:\n\s*)?(\d{7,8})', full_text)
    so_no = match_so.group(1) if match_so else ""
    if so_no and len(so_no) < 8:
        so_no = so_no.zfill(8)

    # 3. Ghi chú (Remarks)
    match_remarks = re.search(r'\(Remarks\)\s*(?:\n\s*)?:?\s*(?:\n\s*)?([^\n]+)', full_text)
    remarks_raw = match_remarks.group(1).strip() if match_remarks else ""
    
    remarks_clean = remarks_raw.replace(',', ' ').strip()
    remarks_clean = re.sub(r'[<>:"/\\|?*]', '', remarks_clean)
    remarks_clean = re.sub(r'\s+', ' ', remarks_clean)
    
    if not remarks_clean:
        match_service = re.search(r'1\s+([^\n\d]+?)\s+\d+[\.,]', full_text)
        remarks_clean = match_service.group(1).strip() if match_service else "HOA DON BANK VCB"
        remarks_clean = re.sub(r'[<>:"/\\|?*]', '', remarks_clean)

    formatted_name = f"{ngay_ky_clean}-{so_no}-{remarks_clean}"
    return {
        'ngay_ky_raw': ngay_ky_raw,
        'ngay_ky_clean': ngay_ky_clean,
        'so_no': so_no,
        'remarks_raw': remarks_raw,
        'remarks_clean': remarks_clean,
        'formatted_name': formatted_name
    }

def record_to_accounting_db(invoices, db_path=DEFAULT_DB_PATH):
    """Tự động phân loại tài khoản và ghi nhận vào bảng nhat_ky_chung trong SQLite."""
    if not os.path.exists(db_path):
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    added_count = 0
    
    for inv in invoices:
        so_hd = f"HD{inv['so_no']}"
        ngay_hd = inv['ngay_hd_iso']
        remarks = inv['remarks']
        amount = inv['amount']
        vat = inv['vat']
        total = inv['total']
        
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
            cursor.execute("SELECT id FROM nhat_ky_chung WHERE so_chung_tu = ? AND tk_no = ?", (entry[1], entry[4]))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO nhat_ky_chung (ngay_ghi_so, so_chung_tu, ngay_chung_tu, dien_giai, tk_no, tk_co, so_tien)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, entry)
                added_count += 1
                
    conn.commit()
    conn.close()
    print(f"-> Đã đồng bộ {added_count} bút toán mới vào Sổ Nhật Ký Chung ({db_path}).")

def export_summary_excel(invoices, output_file):
    """Xuất Bảng kê chi tiết hóa đơn ra file Excel định dạng chuẩn."""
    rows = []
    for idx, inv in enumerate(invoices, 1):
        is_loan = any(k in inv['remarks'].lower() for k in ['lai vay', 'lãi vay', 'tai khoan vay', 'khoan vay'])
        tk_no = '635' if is_loan else '6422'
        rows.append({
            'STT': idx,
            'Ngày Hóa Đơn': inv['ngay_hd'],
            'Ngày Ký': inv['ngay_ky'],
            'Mẫu Số': '1',
            'Ký Hiệu': inv.get('serialNo', 'K26TEA'),
            'Số Hóa Đơn': inv['so_no'],
            'Nhà Cung Cấp': 'Ngân hàng TMCP Ngoại thương Việt Nam (VCB)',
            'MST Bên Bán': '0100112437-016',
            'Hình Thức': 'Ủy nhiệm chi / Giấy báo nợ',
            'Mã Hàng': 'LVA' if is_loan else 'PDV',
            'Nội Dung / Ghi Chú': inv['remarks'],
            'Thành Tiền (VND)': inv['amount'],
            'Thuế Suất': 'KCT' if is_loan else ('10%' if inv['vat'] > 0 else '0%'),
            'Tiền Thuế (VND)': inv['vat'],
            'Tổng Thanh Toán (VND)': inv['total'],
            'TK Nợ': tk_no,
            'TK Có': '1121',
            'TK Thuế': '1331' if inv['vat'] > 0 else '',
            'Tên File PDF': f"{inv['formatted_name']}.pdf",
            'Tên File XML': f"{inv['formatted_name']}.xml"
        })
        
    df = pd.DataFrame(rows)
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Hoa_Don_Bank')
        ws = writer.sheets['Hoa_Don_Bank']
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = col[0].column_letter
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)
            
    print(f"-> Đã xuất Bảng kê Excel chi tiết: {output_file}")

def run_direct_api(month_str="10/2026", account="", fee_only=False, headed=False, force=False, sync_db=True):
    """
    Thực thi tải và hạch toán toàn bộ hóa đơn trong tháng bằng Direct API.
    """
    m, y = month_str.split('/')
    month_num = int(m)
    year_num = int(y)
    
    # Tính ngày đầu tháng và cuối tháng
    last_day = calendar.monthrange(year_num, month_num)[1]
    from_date = f"{year_num}-{month_num:02d}-01"
    to_date = f"{year_num}-{month_num:02d}-{last_day:02d}"
    
    target_dir = os.path.join(BASE_BANK_DIR, f"{year_num}-{month_num:02d}")
    os.makedirs(target_dir, exist_ok=True)
    
    print("\n" + "="*85)
    print(f"  HỆ THỐNG TỰ ĐỘNG HÓA HÓA ĐƠN BANK VIETCOMBANK (DIRECT REST API)")
    print(f"  Kỳ tính thuế / Tháng: {month_str} (Từ {from_date} đến {to_date})")
    if account:
        print(f"  Số tài khoản lọc: {account}")
    if fee_only:
        print(f"  Bộ lọc: Chỉ lấy phí dịch vụ (loại trừ các khoản thu lãi vay)")
    print(f"  Thư mục đích: {target_dir}")
    print("="*85 + "\n")
    
    start_time = time.time()
    processed_list = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel='chrome',
            headless=not headed,
            args=['--disable-http2', '--ignore-certificate-errors', '--no-sandbox']
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        
        # Thiết lập phiên TLS/WAF ban đầu
        print("1. Đang kết nối máy chủ Vietcombank và thiết lập phiên bảo mật...")
        page.goto('https://einvoice.vietcombank.com.vn/', wait_until='networkidle')
        
        # 1. Đăng nhập trực tiếp qua API
        if not DEFAULT_USERNAME or not DEFAULT_PASSWORD:
            print("LỖI BẢO MẬT: Chưa cấu hình VCB_USERNAME và VCB_PASSWORD trong file .env hoặc biến môi trường!")
            print("Vui lòng tạo file .env theo mẫu .env.example và điền thông tin tài khoản.")
            browser.close()
            return []
            
        print("2. Đang gửi yêu cầu đăng nhập mã hóa AES...")
        login_enc = aes_encrypt({"userName": DEFAULT_USERNAME, "password": DEFAULT_PASSWORD})
        login_res = page.evaluate("""async (enc) => {
            const resp = await fetch("https://gw-einvoice.vietcombank.com.vn/api/system/account/login-portal", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ data: enc })
            });
            return await resp.json();
        }""", login_enc)
        
        token = login_res.get('accessToken')
        if not token:
            print("Đăng nhập thất bại:", login_res)
            browser.close()
            return []
            
        print("-> Đăng nhập thành công! Đã cấp phát Bearer Token.")
        
        # 2. Truy vấn danh sách hóa đơn qua API
        print(f"3. Đang truy vấn toàn bộ hóa đơn từ {from_date} đến {to_date}...")
        query_enc = aes_encrypt({
            "type": 1,
            "invoiceStatus": None,
            "createFromDate": from_date,
            "createToDate": to_date,
            "textSearch": "",
            "invoiceNo": "",
            "fromNumber": None,
            "toNumber": None,
            "transactionId": "",
            "buyerBankAccount": account or "",
            "skipCount": 0,
            "maxResultCount": 100,
            "totalCount": 0
        })

        
        query_res = page.evaluate("""async (args) => {
            const resp = await fetch("https://gw-einvoice.vietcombank.com.vn/api/portal/PortalApiService/portal-private", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + args.token
                },
                body: JSON.stringify({ data: args.enc })
            });
            return await resp.json();
        }""", {'token': token, 'enc': query_enc})
        
        items = query_res.get('items', [])
        print(f"-> Tìm thấy {len(items)} hóa đơn thuộc Tháng {month_str}.\n")
        
        # 3. Tải và xử lý từng hóa đơn
        for idx, item in enumerate(items, 1):
            inv_no = item['invoiceNo']
            inv_date_raw = item['invoiceDate'][:10] # yyyy-mm-dd
            d_parts = inv_date_raw.split('-')
            ngay_hd = f"{d_parts[2]}/{d_parts[1]}/{d_parts[0]}"
            ngay_hd_iso = inv_date_raw
            
            # Chuẩn bị payload tải
            dl_pdf_enc = aes_encrypt({
                "templateNo": item['templateNo'],
                "serialNo": item['serialNo'],
                "invoiceNo": inv_no,
                "id": item['id']
            })
            dl_xml_enc = aes_encrypt({
                "templateNo": item['templateNo'],
                "serialNo": item['serialNo'],
                "invoiceNo": inv_no,
                "id": item['id'],
                "source": 8
            })
            
            # Tải đồng thời cả PDF và XML qua API
            files_res = page.evaluate("""async (args) => {
                const pResp = await fetch("https://gw-einvoice.vietcombank.com.vn/api/portal/PortalApiService/download/private/unofficial", {
                    method: "POST",
                    headers: { "Content-Type": "application/json", "Authorization": "Bearer " + args.token },
                    body: JSON.stringify({ data: args.pdfEnc })
                });
                const pJson = await pResp.json();
                
                const xResp = await fetch("https://gw-einvoice.vietcombank.com.vn/api/portal/PortalApiService/download/private/xml", {
                    method: "POST",
                    headers: { "Content-Type": "application/json", "Authorization": "Bearer " + args.token },
                    body: JSON.stringify({ data: args.xmlEnc })
                });
                const xJson = await xResp.json();
                
                return { pdfB64: pJson.fileBytes, xmlB64: xJson.fileBytes };
            }""", {'token': token, 'pdfEnc': dl_pdf_enc, 'xmlEnc': dl_xml_enc})
            
            if not files_res.get('pdfB64'):
                print(f"[{idx}/{len(items)}] Không nhận được dữ liệu PDF cho HĐ {inv_no}!")
                continue
                
            raw_pdf_bytes = base64.b64decode(files_res['pdfB64'])
            raw_xml_bytes = base64.b64decode(files_res['xmlB64']) if files_res.get('xmlB64') else None
            
            # Đọc metadata từ PDF
            meta = parse_pdf_metadata(raw_pdf_bytes)
            
            # Nếu người dùng chỉ muốn lấy hóa đơn phí dịch vụ, bỏ qua các hóa đơn thu lãi vay
            if fee_only and any(kw in meta['remarks_clean'].lower() for kw in ['thu lai', 'lai tai khoan vay', 'lai vay', 'lãi']):
                print(f"[{idx}/{len(items)}] BỎ QUA (Phí dịch vụ only): {meta['so_no']} - {meta['remarks_clean']}")
                continue
                
            # Bóc tách chính xác số tiền từ dữ liệu XML gốc
            amount = float(item.get('totalAmount', 0))
            vat = 0.0
            total = 0.0
            
            if raw_xml_bytes:
                try:
                    import xml.etree.ElementTree as ET
                    xml_root = ET.fromstring(raw_xml_bytes)
                    th_tien = xml_root.find('.//ThTien')
                    if th_tien is None:
                        th_tien = xml_root.find('.//TgTCThue')
                    t_thue = xml_root.find('.//TThue')
                    if t_thue is None:
                        t_thue = xml_root.find('.//TgTThue')
                    tg_tt = xml_root.find('.//TgTTTBSo')
                    
                    if th_tien is not None and th_tien.text and th_tien.text.strip():
                        amount = float(th_tien.text.strip())
                    if t_thue is not None and t_thue.text and t_thue.text.strip():
                        vat = float(t_thue.text.strip())
                    if tg_tt is not None and tg_tt.text and tg_tt.text.strip():
                        total = float(tg_tt.text.strip())
                except Exception:
                    pass
                    
            if total == 0:
                total = amount + vat
            if vat == 0 and total > amount:
                vat = round(total - amount, 2)

                
            # Lưu file vào thư mục đích
            pdf_path = os.path.join(target_dir, f"{meta['formatted_name']}.pdf")
            xml_path = os.path.join(target_dir, f"{meta['formatted_name']}.xml")
            
            with open(pdf_path, "wb") as f:
                f.write(raw_pdf_bytes)
            if raw_xml_bytes:
                with open(xml_path, "wb") as f:
                    f.write(raw_xml_bytes)
                    
            print(f"[{idx}/{len(items)}] ĐÃ TẢI & ĐỔI TÊN THÀNH CÔNG:")
            print(f"    - Ngày HĐ: {ngay_hd} | Ngày ký: {meta['ngay_ky_raw']} | Số HĐ: {meta['so_no']}")
            print(f"    - Ghi chú: {meta['remarks_clean']}")
            print(f"    - Tiền chưa VAT: {amount:,.0f} VND | Thuế VAT: {vat:,.0f} VND | Tổng: {total:,.0f} VND")
            print(f"    - File: {meta['formatted_name']}.pdf\n")
            
            processed_list.append({
                'ngay_hd': ngay_hd,
                'ngay_hd_iso': ngay_hd_iso,
                'ngay_ky': meta['ngay_ky_raw'],
                'serialNo': item['serialNo'],
                'so_no': meta['so_no'],
                'remarks': meta['remarks_clean'],
                'formatted_name': meta['formatted_name'],
                'amount': amount,
                'vat': vat,
                'total': total,
                'pdf_path': pdf_path,
                'xml_path': xml_path
            })
            
        browser.close()
        
    # 4. Tự động hạch toán vào SQLite
    if sync_db and processed_list:
        record_to_accounting_db(processed_list)
        
    # 5. Xuất file Excel tổng hợp
    if processed_list:
        excel_output = os.path.join(target_dir, f"Bang_Ke_Hoa_Don_Bank_Thang_{month_num}_{year_num}.xlsx")
        export_summary_excel(processed_list, excel_output)
        
    elapsed = time.time() - start_time
    print("="*85)
    print(f"  HOÀN THÀNH: XỬ LÝ {len(processed_list)}/{len(items)} HÓA ĐƠN THÁNG {month_str} TRONG {elapsed:.2f} GIÂY!")
    print("="*85 + "\n")
    return processed_list

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Tự động tải và hạch toán hóa đơn điện tử VCB theo tháng qua Direct API.")
    parser.add_argument("month", nargs="?", default="10/2026", help="Tháng/Năm cần xử lý (định dạng MM/YYYY, ví dụ: 10/2026)")
    parser.add_argument("--account", default="", help="Lọc theo Số tài khoản ngân hàng (ví dụ: 1035325735)")
    parser.add_argument("--fee-only", action="store_true", help="Chỉ tải các hóa đơn phí dịch vụ (loại bỏ hóa đơn thu lãi vay)")
    parser.add_argument("--headed", action="store_true", help="Chạy hiển thị trình duyệt")
    parser.add_argument("--force", action="store_true", help="Ghi đè tệp tin nếu đã tồn tại")
    parser.add_argument("--no-db", action="store_true", help="Không tự động ghi vào ketoan.db")
    
    args = parser.parse_args()
    run_direct_api(
        month_str=args.month,
        account=args.account,
        fee_only=args.fee_only,
        headed=args.headed,
        force=args.force,
        sync_db=not args.no_db
    )
