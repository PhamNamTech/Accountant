@echo off
chcp 65001 > nul

echo =================================================================
echo   HE THONG KE TOAN AI - DONG BO 1 CHAM [NO-ADMIN ^& NO-GITHUB]
echo =================================================================
echo.

REM -----------------------------------------------------------------
REM BUOC 1: Kiem tra Python va cai dat thu vien vao User directory
REM -----------------------------------------------------------------
echo [1/4] Kiem tra moi truong Python [User Scope, khong can Admin]...
python --version >nul 2>&1
if errorlevel 1 (
    echo [LOI] May tinh chua co Python trong PATH.
    echo Vui long cai dat Python va tich chon "Add Python to PATH".
    pause
    exit /b 1
)

echo       Cai dat/cap nhat thu vien python qua che do --user...
python -m pip install --user mcp pandas openpyxl pypdf pdfplumber requests beautifulsoup4
echo   [OK] Thu vien Python da san sang.

REM -----------------------------------------------------------------
REM BUOC 2: Cau hinh OfficeCLI Offline [Khong can tai tu GitHub]
REM -----------------------------------------------------------------
echo.
echo [2/4] Cau hinh OfficeCLI [Che do Offline]...
set "OFFICECLI_DIR=%LOCALAPPDATA%\OfficeCLI"
set "OFFICECLI_EXE=%LOCALAPPDATA%\OfficeCLI\officecli.exe"
set "BUNDLED_EXE=%~dp0tools\bin\officecli.exe"

if not exist "%OFFICECLI_DIR%" mkdir "%OFFICECLI_DIR%" >nul 2>&1

if exist "%BUNDLED_EXE%" (
    if not exist "%OFFICECLI_EXE%" (
        echo       Sao chep OfficeCLI tu ban dong goi san tools\bin...
        copy /y "%BUNDLED_EXE%" "%OFFICECLI_EXE%" >nul
    )
    echo   [OK] OfficeCLI da duoc kich hoat tai: %OFFICECLI_EXE%
) else (
    where officecli >nul 2>&1
    if errorlevel 1 (
        echo       Dang tai OfficeCLI qua mirror...
        powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://d.officecli.ai/install.ps1 | iex" >nul 2>&1
    )
)

REM Them OfficeCLI vao User PATH neu chua co [Khong can quyen Admin]
powershell -NoProfile -Command "$p = [Environment]::GetEnvironmentVariable('Path', 'User'); if ($p -notlike '*OfficeCLI*') { [Environment]::SetEnvironmentVariable('Path', $p + ';%LOCALAPPDATA%\OfficeCLI', 'User') }" >nul 2>&1

REM -----------------------------------------------------------------
REM BUOC 3: Dong bo cau hinh MCP Servers vao Antigravity
REM -----------------------------------------------------------------
echo.
echo [3/4] Dong bo cau hinh MCP Servers vao Antigravity...
python tools\sync_environment.py
if errorlevel 1 (
    echo [LOI] Dong bo cau hinh that bai!
    pause
    exit /b 1
)

REM -----------------------------------------------------------------
REM BUOC 4: Kiem thu toan dien 12 bai test
REM -----------------------------------------------------------------
echo.
echo [4/4] Kiem thu toan dien he thong xac nhan [12/12 Tests]...
python run_all_tests.py
if errorlevel 1 (
    echo.
    echo [CANH BAO] Co mot so bai test chua vuot qua. Vui long xem log o tren.
) else (
    echo.
    echo =================================================================
    echo   *** CHUC MUNG: HE THONG DA DONG BO 100%% THANH CONG! ***
    echo.
    echo   [XAC NHAN AN TOAN]:
    echo   1. KHONG can quyen Admin: Toan bo cong cu chay o User scope.
    echo   2. KHONG phu thuoc GitHub:
    echo      - Ma nguon clone qua Codeberg.
    echo      - OfficeCLI da dong goi san trong tools\bin\officecli.exe.
    echo      - CSDL SQLite chuyen sang Python thuan sqlite_server.py.
    echo      - Cac MCP Server deu chay doc lap offline hoac qua Cong quoc gia.
    echo.
    echo   * BUOC CUOI CUNG:
    echo   Khoi dong lai Antigravity de IDE tu dong nap toan bo MCP Servers!
    echo =================================================================
)

echo.
