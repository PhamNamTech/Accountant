r"""
Bộ kích hoạt kiểm thử toàn diện hệ thống Kế toán tại F:\Accountant
Ủy quyền thực thi toàn bộ kịch bản kiểm thử tại tests/run_all_tests.py
"""
import os
import sys
import subprocess

if __name__ == "__main__":
    test_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests", "run_all_tests.py")
    result = subprocess.run([sys.executable, test_script] + sys.argv[1:])
    sys.exit(result.returncode)
