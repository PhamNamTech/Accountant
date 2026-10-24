r"""
Bộ kích hoạt kiểm thử toàn diện hệ thống Kế toán tại F:\Accountant
Ủy quyền thực thi:
1. Bộ 8 bài test lõi kế toán truyền thống (tests/run_all_tests.py)
2. Bộ 4 nhóm test tích hợp mới: VBPL, Tax Verify, Finance & Bank API (tests/test_new_integrations.py)
"""
import os
import sys
import subprocess

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    core_test = os.path.join(base, "tests", "run_all_tests.py")
    new_test = os.path.join(base, "tests", "test_new_integrations.py")

    print("\n>>> CHẠY BỘ KIỂM THỬ LÕI KẾ TOÁN (8 BÀI TEST)...")
    res1 = subprocess.run([sys.executable, core_test])
    if res1.returncode != 0:
        print("[LỖI] Bộ kiểm thử lõi kế toán thất bại!")
        sys.exit(res1.returncode)

    print("\n>>> CHẠY BỘ KIỂM THỬ TÍCH HỢP MỚI (TRA CỨU & XÁC THỰC NGUỒN GỐC)...")
    res2 = subprocess.run([sys.executable, new_test])
    if res2.returncode != 0:
        print("[LỖI] Bộ kiểm thử tích hợp mới thất bại!")
        sys.exit(res2.returncode)

    print("\n=================================================================")
    print("  TOÀN BỘ 12 BÀI KIỂM THỬ HỆ THỐNG ĐÃ VƯỢT QUA 100% ĐẠT CHUẨN!")
    print("=================================================================\n")
    sys.exit(0)
