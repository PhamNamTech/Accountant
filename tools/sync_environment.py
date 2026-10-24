"""
Script tự động cấu hình và đồng bộ toàn bộ môi trường kế toán & MCP Servers
cho dự án Accountant trên bất kỳ máy tính nào.

Chức năng:
1. Tự động nhận diện thư mục dự án hiện tại (không hardcode đường dẫn ổ đĩa F:/ hay C:/).
2. Tự động nhận diện User Profile (%USERPROFILE%) và AppData của Windows.
3. Cập nhật / Ghép (merge) toàn bộ 7 MCP Server của dự án vào file:
   %USERPROFILE%\\.gemini\\config\\mcp_config.json
   (Bảo toàn toàn bộ các MCP server cá nhân khác của người dùng như ffmpeg, capcut, notebooklm...).
4. Tạo đầy đủ cấu trúc thư mục dữ liệu nội bộ (data/, cache/, sources/).
5. Khởi tạo cơ sở dữ liệu SQLite data/database/ketoan.db nếu chưa có.
6. Tự động tạo file .env từ .env.example nếu chưa có.
"""

import os
import sys
import json
import shutil
import sqlite3

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Đường dẫn dự án hiện tại
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR_SLASH = BASE_DIR.replace("\\", "/")

# Thư mục cấu hình Antigravity / Gemini của người dùng
USER_PROFILE = os.environ.get("USERPROFILE") or os.path.expanduser("~")
APPDATA = os.environ.get("APPDATA") or os.path.join(USER_PROFILE, "AppData", "Roaming")
MCP_CONFIG_DIR = os.path.join(USER_PROFILE, ".gemini", "config")
MCP_CONFIG_FILE = os.path.join(MCP_CONFIG_DIR, "mcp_config.json")


def setup_directories():
    """Khởi tạo đầy đủ cấu trúc thư mục làm việc của dự án."""
    dirs_to_create = [
        os.path.join(BASE_DIR, "data", "database"),
        os.path.join(BASE_DIR, "data", "cache", "vbpl"),
        os.path.join(BASE_DIR, "data", "cache", "mst"),
        os.path.join(BASE_DIR, "data", "cache", "exchange_rates"),
        os.path.join(BASE_DIR, "data", "cache", "bank"),
        os.path.join(BASE_DIR, "data", "chung_tu", "hoa_don_mua_vao"),
        os.path.join(BASE_DIR, "data", "chung_tu", "hoa_don_bank"),
        os.path.join(BASE_DIR, "data", "ngan_hang", "sao_ke"),
        os.path.join(BASE_DIR, "data", "so_sach", "danh_muc"),
        os.path.join(BASE_DIR, "data", "so_sach", "bang_ke_hach_toan"),
        os.path.join(BASE_DIR, "sources", "cache"),
        os.path.join(BASE_DIR, "tests", "test_output")
    ]
    for d in dirs_to_create:
        os.makedirs(d, exist_ok=True)
    print("  [✓] Cấu trúc thư mục dữ liệu đã sẵn sàng.")


def init_database():
    """Khởi tạo SQLite ketoan.db nếu chưa tồn tại."""
    db_path = os.path.join(BASE_DIR, "data", "database", "ketoan.db")
    conn = sqlite3.connect(db_path)
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
    cur.execute("""
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_date TEXT NOT NULL,
            voucher_no TEXT NOT NULL,
            description TEXT NOT NULL,
            debit_account TEXT NOT NULL,
            credit_account TEXT NOT NULL,
            amount REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print("  [✓] Cơ sở dữ liệu SQLite data/database/ketoan.db đã sẵn sàng.")


def init_env():
    """Tạo file .env từ .env.example nếu chưa có."""
    env_file = os.path.join(BASE_DIR, ".env")
    example_file = os.path.join(BASE_DIR, ".env.example")
    if not os.path.exists(env_file) and os.path.exists(example_file):
        shutil.copyfile(example_file, env_file)
        print("  [✓] Đã tạo file cấu hình .env từ .env.example.")
    else:
        print("  [✓] File cấu hình .env đã tồn tại.")


def sync_mcp_config():
    """Cập nhật mcp_config.json tự động với đường dẫn động."""
    os.makedirs(MCP_CONFIG_DIR, exist_ok=True)

    config_data = {"mcpServers": {}}
    if os.path.exists(MCP_CONFIG_FILE):
        try:
            with open(MCP_CONFIG_FILE, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                if "mcpServers" not in config_data:
                    config_data["mcpServers"] = {}
        except Exception as e:
            print(f"  [!] Lưu ý: Đọc file mcp_config.json cũ gặp lỗi ({e}). Sẽ tạo mới.")
            config_data = {"mcpServers": {}}

    servers = config_data["mcpServers"]

    # 1. ketoan-vn
    servers["ketoan-vn"] = {
        "command": "python",
        "args": [f"{PROJECT_DIR_SLASH}/tools/ketoan_server.py"],
        "env": {"PYTHONUTF8": "1"}
    }

    # 2. vbpl-lookup
    servers["vbpl-lookup"] = {
        "command": "python",
        "args": [f"{PROJECT_DIR_SLASH}/tools/vbpl_server.py"],
        "env": {"PYTHONUTF8": "1"}
    }

    # 3. tax-verify
    servers["tax-verify"] = {
        "command": "python",
        "args": [f"{PROJECT_DIR_SLASH}/tools/tax_verify_server.py"],
        "env": {"PYTHONUTF8": "1"}
    }

    # 4. finance-tools
    servers["finance-tools"] = {
        "command": "python",
        "args": [f"{PROJECT_DIR_SLASH}/tools/finance_server.py"],
        "env": {"PYTHONUTF8": "1"}
    }

    # 5. bank-api
    servers["bank-api"] = {
        "command": "python",
        "args": [f"{PROJECT_DIR_SLASH}/tools/bank_server.py"],
        "env": {"PYTHONUTF8": "1"}
    }

    # 6. sqlite-ketoan (Chạy bằng Python thuần, không cần Node.js, không cần npm, không cần GitHub hay Admin)
    servers["sqlite-ketoan"] = {
        "command": "python",
        "args": [f"{PROJECT_DIR_SLASH}/tools/sqlite_server.py"],
        "env": {"PYTHONUTF8": "1"}
    }

    # 7. excel-mcp
    servers["excel-mcp"] = {
        "command": "npx",
        "args": ["-y", "@negokaz/excel-mcp-server"]
    }

    # 8. notebooklm (bảo toàn cấu hình nếu đã có, hoặc tạo mới nếu chưa có)
    if "notebooklm" not in servers:
        global_nb_script = os.path.join(APPDATA, "npm", "node_modules", "@leonai", "notebooklm-mcp", "dist", "index.js")
        global_nb_script_slash = global_nb_script.replace("\\", "/")
        servers["notebooklm"] = {
            "command": "node",
            "args": [global_nb_script_slash]
        }

    # Lưu lại mcp_config.json
    with open(MCP_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, ensure_ascii=False, indent=2)

    print(f"  [✓] Đã đồng bộ 7 MCP Server vào: {MCP_CONFIG_FILE}")
    for name in ["ketoan-vn", "vbpl-lookup", "tax-verify", "finance-tools", "bank-api", "sqlite-ketoan", "excel-mcp"]:
        print(f"      + {name}")


def main():
    print("=" * 65)
    print("  ĐỒNG BỘ CẤU HÌNH DỰ ÁN KẾ TOÁN & MCP SERVERS CHO MÁY MỚI")
    print(f"  Thư mục dự án: {BASE_DIR}")
    print(f"  Tài khoản người dùng: {USER_PROFILE}")
    print("=" * 65)

    print("\n[Bước 1/4] Khởi tạo cấu trúc thư mục dữ liệu...")
    setup_directories()

    print("\n[Bước 2/4] Khởi tạo cơ sở dữ liệu SQLite...")
    init_database()

    print("\n[Bước 3/4] Kiểm tra cấu hình .env...")
    init_env()

    print("\n[Bước 4/4] Đồng bộ cấu hình MCP Servers vào Antigravity...")
    sync_mcp_config()

    print("\n" + "=" * 65)
    print("  HOÀN TẤT ĐỒNG BỘ MCP VÀ CẤU HÌNH THÀNH CÔNG!")
    print("=" * 65)


if __name__ == "__main__":
    main()
