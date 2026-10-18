import sys
import os
import time
import json
import base64
import io
import re
from playwright.sync_api import sync_playwright
import pypdf
from dotenv import load_dotenv

# Tự động nạp biến môi trường từ .env
load_dotenv()

sys.stdout.reconfigure(encoding='utf-8')

TARGET_DATE = "09/10/2026"
USERNAME = os.environ.get("VCB_USERNAME", "")
PASSWORD = os.environ.get("VCB_PASSWORD", "")
OUTPUT_DIR = r"F:\Accountant\data\chung_tu\hoa_don_bank\2026-10"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def parse_pdf_metadata(pdf_bytes):
    """
    Đọc trực tiếp nội dung file PDF hóa đơn Vietcombank để trích xuất các trường:
    1. Ngày ký (Signing Date) -> chuyển thành định dạng DDMMYYYY (ví dụ: 10/10/2026 -> 10102026)
    2. Số (Invoice No) -> chuẩn hóa 8 chữ số (ví dụ: 01405135)
    3. Ghi chú (Remarks) -> loại bỏ ký tự đặc biệt/dấu phẩy không hợp lệ trong tên file (ví dụ: CC004 C009 THU PHI TT UNC VA BK GNN 16)
    """
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    full_text = '\n'.join([p.extract_text() for p in reader.pages])
    
    # 1. Trích xuất Ngày ký
    match_ngay_ky = re.search(r'Ngày ký\s*:\s*(?:\n\s*)*(\d{2}/\d{2}/\d{4})', full_text)
    if not match_ngay_ky:
        match_ngay_ky = re.search(r'(\d{2}/\d{2}/\d{4})', full_text)
    ngay_ky_raw = match_ngay_ky.group(1) if match_ngay_ky else ""
    ngay_ky_clean = ngay_ky_raw.replace('/', '')
    
    # 2. Trích xuất Số hóa đơn (No)
    match_so = re.search(r'Số\s*(?:\n\s*)?\(No\)\s*(?:\n\s*)?:?\s*(?:\n\s*)?(\d{7,8})', full_text)
    so_no = match_so.group(1) if match_so else ""
    if so_no and len(so_no) < 8:
        so_no = so_no.zfill(8)
        
    # 3. Trích xuất Ghi chú (Remarks)
    match_remarks = re.search(r'\(Remarks\)\s*(?:\n\s*)?:?\s*(?:\n\s*)?([^\n]+)', full_text)
    remarks_raw = match_remarks.group(1).strip() if match_remarks else ""
    # Chuẩn hóa: loại bỏ dấu phẩy, ký tự cấm của Windows, chuẩn hóa khoảng trắng
    remarks_clean = remarks_raw.replace(',', ' ').strip()
    remarks_clean = re.sub(r'[<>:"/\\|?*]', '', remarks_clean)
    remarks_clean = re.sub(r'\s+', ' ', remarks_clean)
    
    formatted_name = f"{ngay_ky_clean}-{so_no}-{remarks_clean}"
    return {
        'ngay_ky_raw': ngay_ky_raw,
        'ngay_ky_clean': ngay_ky_clean,
        'so_no': so_no,
        'remarks_raw': remarks_raw,
        'remarks_clean': remarks_clean,
        'formatted_name': formatted_name
    }

def run():
    print(f"=== BẮT ĐẦU QUY TRÌNH TỰ ĐỘNG HÓA TẢI & ĐẶT TÊN HÓA ĐƠN VCB NGÀY {TARGET_DATE} ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel='chrome',
            headless=False,
            args=['--disable-http2', '--ignore-certificate-errors']
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            accept_downloads=True
        )
        page = context.new_page()
        
        # Step 1: Truy cập trang
        print("Step 1: Truy cập https://einvoice.vietcombank.com.vn/ ...")
        page.goto('https://einvoice.vietcombank.com.vn/', wait_until='networkidle')
        time.sleep(1)
        
        # Step 2: Click menu Đăng nhập
        print("Step 2: Click menu 'Đăng nhập'...")
        page.locator("li:has-text('Đăng nhập'), a:has-text('Đăng nhập')").first.click()
        time.sleep(1)
        
        # Step 3: Nhập tài khoản và đăng nhập
        print(f"Step 3: Nhập username ({USERNAME}), password và đăng nhập...")
        page.fill("input[placeholder='Tên đăng nhập']", USERNAME)
        page.fill("input[placeholder='Mật khẩu']", PASSWORD)
        page.locator("button:has-text('Đăng nhập')").first.click()
        time.sleep(3)
        page.wait_for_load_state('networkidle')
        print("Đăng nhập thành công!")
        
        # Step 4: Tìm dòng có ngày hóa đơn chỉ định
        print(f"Step 4: Tìm dòng hóa đơn có ngày lập {TARGET_DATE}...")
        target_row = page.locator(f"tr:has-text('{TARGET_DATE}')").first
        if target_row.count() == 0:
            raise Exception(f"Không tìm thấy dòng hóa đơn có ngày {TARGET_DATE}!")
            
        row_text = target_row.inner_text().replace('\n', ' | ')
        print(f"Dữ liệu bảng: {row_text}")
        
        buttons = target_row.locator("button").all()
        btn_xml = buttons[0]
        btn_pdf = buttons[1]
        
        # Tải file XML gốc
        xml_bytes = None
        try:
            print("Đang tải dữ liệu XML gốc...")
            with page.expect_response(lambda r: "download" in r.url and "unofficial" not in r.url, timeout=10000) as xml_resp_info:
                btn_xml.click()
            xml_resp = xml_resp_info.value
            xml_json = xml_resp.json()
            if xml_json.get('fileBytes'):
                xml_bytes = base64.b64decode(xml_json['fileBytes'])
                print(f"Đã nhận dữ liệu XML ({len(xml_bytes)} bytes).")
        except Exception as e:
            print("Lưu ý về XML:", e)
            
        # Step 5: Tải file PDF
        print("Step 5: Thực hiện Xuất PDF...")
        with page.expect_response(lambda r: "download/private/unofficial" in r.url, timeout=15000) as resp_info:
            btn_pdf.click()
            
        pdf_resp = resp_info.value
        pdf_data = pdf_resp.json()
        raw_pdf_bytes = base64.b64decode(pdf_data['fileBytes'])
        print(f"Đã nhận dữ liệu PDF ({len(raw_pdf_bytes)} bytes).")
        
        # Đọc nội dung PDF để sinh tên file chuẩn xác 100% theo nội dung
        print("\n--- Đọc và phân tích trực tiếp nội dung PDF ---")
        meta = parse_pdf_metadata(raw_pdf_bytes)
        print(f"  + Ngày ký trích xuất : {meta['ngay_ky_raw']} -> {meta['ngay_ky_clean']}")
        print(f"  + Số hóa đơn (No)    : {meta['so_no']}")
        print(f"  + Ghi chú (Remarks)  : {meta['remarks_raw']} -> {meta['remarks_clean']}")
        print(f"  ==> Tên file sinh ra : {meta['formatted_name']}")
        
        # Step 6: Lưu và đổi tên file PDF & XML
        pdf_filename = f"{meta['formatted_name']}.pdf"
        target_pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)
        with open(target_pdf_path, "wb") as f:
            f.write(raw_pdf_bytes)
        print(f"\nStep 6: ĐÃ LƯU & ĐỔI TÊN FILE PDF THÀNH CÔNG:")
        print(f"  --> {target_pdf_path}")
        
        if xml_bytes:
            xml_filename = f"{meta['formatted_name']}.xml"
            target_xml_path = os.path.join(OUTPUT_DIR, xml_filename)
            with open(target_xml_path, "wb") as f:
                f.write(xml_bytes)
            print(f"  --> ĐÃ LƯU & ĐỔI TÊN FILE XML THÀNH CÔNG:")
            print(f"  --> {target_xml_path}")
            
        browser.close()
        print("\n=== HOÀN TẤT THỰC THI ===")
        return meta

if __name__ == '__main__':
    run()
