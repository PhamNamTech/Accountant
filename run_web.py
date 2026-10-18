"""
Kịch bản khởi chạy Hệ Thống Web Kế Toán Việt Nam (Vietnam Accounting Suite)
Tích hợp Frontend React (ThreeUI, Hairline, Lucian UX/UI) & Backend FastAPI
Địa chỉ truy cập mặc định: http://127.0.0.1:8000
"""

import os
import sys
import webbrowser
import uvicorn

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8000
    url = f"http://{host}:{port}"
    print("=" * 70)
    print("   HỆ THỐNG TỰ ĐỘNG HÓA HÓA ĐƠN BANK VIETCOMBANK (XML & PDF)")
    print(f"   Khởi động máy chủ Web tại: {url}")
    print(f"   Tài liệu Swagger API tại:   {url}/docs")
    print("=" * 70)
    
    # Tự động mở trình duyệt nếu muốn
    # webbrowser.open(url)
    
    uvicorn.run("web.backend.main:app", host=host, port=port, reload=False)
