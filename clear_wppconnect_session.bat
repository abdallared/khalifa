@echo off
REM ============================================
REM Clear WPPConnect Session & Tokens
REM حذف جميع جلسات وتوكنات WPPConnect
REM ============================================

echo ============================================
echo 🗑️ Clearing WPPConnect Session
echo ============================================
echo.

REM التحقق من وجود مجلد tokens
if exist "wppconnect-server\tokens" (
    echo 📂 Found tokens folder
    echo 🗑️ Deleting all tokens...
    
    REM حذف جميع الملفات والمجلدات داخل tokens
    rd /s /q "wppconnect-server\tokens"
    
    REM إعادة إنشاء المجلد فارغاً
    mkdir "wppconnect-server\tokens"
    
    echo ✅ Tokens cleared successfully
) else (
    echo ⚠️ Tokens folder not found
    mkdir "wppconnect-server\tokens"
    echo ✅ Created empty tokens folder
)

echo.

REM حذف ملفات .data.json إن وجدت
if exist "wppconnect-server\*.data.json" (
    echo 🗑️ Deleting .data.json files...
    del /q "wppconnect-server\*.data.json"
    echo ✅ .data.json files deleted
)

echo.

REM حذف مجلد uploads القديم (اختياري)
if exist "wppconnect-server\uploads" (
    echo 📂 Found uploads folder
    echo ❓ Do you want to clear uploads folder too? (Y/N)
    set /p clear_uploads=
    
    if /i "%clear_uploads%"=="Y" (
        echo 🗑️ Deleting uploads...
        rd /s /q "wppconnect-server\uploads"
        mkdir "wppconnect-server\uploads"
        echo ✅ Uploads cleared
    ) else (
        echo ⏭️ Skipping uploads folder
    )
)

echo.
echo ============================================
echo ✅ WPPConnect Session Cleared!
echo ============================================
echo.
echo 📝 Next Steps:
echo   1. Start WPPConnect server
echo   2. Scan QR code with NEW phone number
echo   3. System will create new session
echo.
echo ============================================
pause

