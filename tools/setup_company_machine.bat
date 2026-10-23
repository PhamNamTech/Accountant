@echo off
chcp 65001 > nul
echo =======================================================
echo   THIET LAP MOI TRUONG MAY CONG TY CHO DU AN KETOAN
echo =======================================================
echo.

echo [1/3] Kiem tra Python...
python --version
if %errorlevel% neq 0 (
    echo [CANH BAO] May cong ty chua cai Python hoac chua them vao PATH.
    echo Vui long cai Python 3.10 tro len de chay cac cong cu ke toan.
) else (
    echo Dang cai dat cac thu vien Python can thiet...
    pip install pandas openpyxl pypdf pdfplumber
)

echo.
echo [2/3] Kiem tra va cai dat OfficeCLI...
where officecli >nul 2>nul
if %errorlevel% neq 0 (
    echo Dang cai dat OfficeCLI cho may cong ty...
    powershell -Command "irm https://d.officecli.ai/install.ps1 | iex"
) else (
    echo OfficeCLI da duoc cai dat.
)

echo.
echo [3/3] Chay kiem thu he thong xac nhan...
python run_all_tests.py

echo.
echo =======================================================
echo   HOAN TAT! May cong ty da san sang lam viec.
echo =======================================================
pause
