@echo off
echo ================================
echo   Password Manager
echo ================================
echo.

REM Kiểm tra Python có sẵn không
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python chua duoc cai dat!
    echo Vui long tai Python tu https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [INFO] Dang kiem tra thu vien...

REM Kiểm tra thư viện
python -c "import cryptography, argon2, pyperclip, tkinter" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Mot so thu vien chua duoc cai dat!
    echo [INFO] Dang tu dong cai dat...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Khong the cai dat thu vien!
        echo Vui long chay: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
)

echo [OK] Tat ca thu vien da san sang!
echo [INFO] Dang khoi dong ung dung...
echo.

REM Chạy ứng dụng
python -m app.main

if errorlevel 1 (
    echo.
    echo [ERROR] Ung dung gap loi!
    pause
)

