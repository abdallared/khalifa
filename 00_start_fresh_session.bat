@echo off
REM ============================================
REM Start Fresh WPPConnect Session
REM بدء جلسة جديدة مع رقم هاتف جديد
REM ============================================

setlocal enabledelayedexpansion

REM تعريف الألوان
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "RESET=[0m"

cls
echo ============================================
echo %BLUE%🚀 Starting Fresh WPPConnect Session%RESET%
echo ============================================
echo.

echo %YELLOW%[INFO]%RESET% This will start a NEW session with a NEW phone number
echo.

set SESSION_NAME=khalifa-pharmacy
echo %YELLOW%[ACTION]%RESET% Stopping any running servers on ports 3000 and 8000...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr :3000') do taskkill /PID %%p /F >nul 2>&1
for /f "tokens=5" %%p in ('netstat -ano ^| findstr :8000') do taskkill /PID %%p /F >nul 2>&1
echo %GREEN%[OK]%RESET% Ports cleared
echo.

echo %YELLOW%[ACTION]%RESET% Clearing WhatsApp session tokens...
if exist "wppconnect-server\tokens" (
    rd /s /q "wppconnect-server\tokens"
)
mkdir "wppconnect-server\tokens"
echo %GREEN%[OK]%RESET% Tokens folder reset
echo.

echo %YELLOW%[ACTION]%RESET% Clearing WPPConnect data files...
del /q "wppconnect-server\*.data.json" >nul 2>&1
echo %GREEN%[OK]%RESET% Data files cleared
echo.

echo %YELLOW%[ACTION]%RESET% Clearing uploads...
if exist "wppconnect-server\uploads" rd /s /q "wppconnect-server\uploads"
mkdir "wppconnect-server\uploads"
echo %GREEN%[OK]%RESET% Uploads folder reset
echo.

REM التحقق من Node.js
echo %YELLOW%[CHECKING]%RESET% Checking Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%[ERROR] Node.js is not installed%RESET%
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
echo %GREEN%[OK]%RESET% Node.js %NODE_VERSION% found
echo.

REM التحقق من Python
echo %YELLOW%[CHECKING]%RESET% Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%[ERROR] Python is not installed%RESET%
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo %GREEN%[OK]%RESET% %PYTHON_VERSION% found
echo.

REM بدء WPPConnect Server
echo %YELLOW%[STARTING]%RESET% Starting WPPConnect Server...
echo.
cd wppconnect-server
start "WPPConnect Server - NEW SESSION" cmd /k "node server.js"
cd ..
timeout /t 5 /nobreak >nul
echo %GREEN%[OK]%RESET% WPPConnect Server window opened
echo.

REM بدء Django Backend
echo %YELLOW%[STARTING]%RESET% Starting Django Backend...
echo.
cd System
start "Django Backend" cmd /k "python manage.py runserver 0.0.0.0:8000"
cd ..
timeout /t 3 /nobreak >nul
echo %GREEN%[OK]%RESET% Django Backend window opened
echo.

echo ============================================
echo %GREEN%[SUCCESS]%RESET% Fresh Session Started!
echo ============================================
echo.
echo %BLUE%📱 Next Steps:%RESET%
echo   1. In WPPConnect window, scan the QR with your NEW phone
echo   2. Wait for connection confirmation (status becomes CONNECTED)
echo   3. Verify: http://localhost:3000/health
echo   4. Open:   http://localhost:8000/login/
echo.
echo %YELLOW%⚠️ Important:%RESET%
echo   - Use a DIFFERENT phone number than before
echo   - Keep the terminal windows open
echo   - Don't close until QR is scanned
echo.
echo %BLUE%🌐 Access Points:%RESET%
echo   - Django:     http://localhost:8000/login/
echo   - WPPConnect: http://localhost:3000/health
echo.
echo ============================================
echo.

endlocal
pause
