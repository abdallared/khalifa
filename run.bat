@echo off
REM ============================================
REM Run Script for Khalifa Pharmacy System
REM ?? ??? ????? ???? ??????? ?????
REM ============================================
REM Run.bat - ?????? Django Backend ? WPPConnect Server

setlocal enabledelayedexpansion

REM ????? ??????
set ROOT_DIR=%~dp0
set SYSTEM_DIR=%ROOT_DIR%System
set WPPCONNECT_DIR=%ROOT_DIR%wppconnect-server

REM ?????
set "GREEN=[92m"
set "BLUE=[94m"
set "YELLOW=[93m"
set "RED=[91m"
set "RESET=[0m"

cls
echo.
echo ============================================
echo   ???? ??????? ????? - ?? ?????
echo   Khalifa Pharmacy System - Run Script
echo ============================================
echo.

REM ?????? ?? ???? ???????? ????????
if not exist "%SYSTEM_DIR%" (
    echo %RED%[ERROR] System folder not found: %SYSTEM_DIR%%RESET%
    pause
    exit /b 1
)

if not exist "%WPPCONNECT_DIR%" (
    echo %RED%[ERROR] WPPConnect folder not found: %WPPCONNECT_DIR%%RESET%
    pause
    exit /b 1
)

echo %BLUE%[INFO]%RESET% Root Directory: %ROOT_DIR%
echo %BLUE%[INFO]%RESET% System Directory: %SYSTEM_DIR%
echo %BLUE%[INFO]%RESET% WPPConnect Directory: %WPPCONNECT_DIR%
echo.

REM ?????? ?? Python
echo %YELLOW%[CHECKING]%RESET% Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%[ERROR] Python is not installed or not in PATH%RESET%
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo %GREEN%[OK]%RESET% Python %PYTHON_VERSION% found

REM ?????? ?? Node.js
echo %YELLOW%[CHECKING]%RESET% Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%[ERROR] Node.js is not installed or not in PATH%RESET%
    echo Please install Node.js 14+ from https://nodejs.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
echo %GREEN%[OK]%RESET% Node.js %NODE_VERSION% found

REM ?????? ?? npm
echo %YELLOW%[CHECKING]%RESET% Checking npm installation...
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%[ERROR] npm is not installed or not in PATH%RESET%
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('npm --version 2^>^&1') do set NPM_VERSION=%%i
echo %GREEN%[OK]%RESET% npm %NPM_VERSION% found
echo.

REM ?????? ?? Django
echo %YELLOW%[CHECKING]%RESET% Checking Django installation...
cd /d "%SYSTEM_DIR%"
python -m django --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%[ERROR] Django is not installed%RESET%
    echo Please run: pip install -r requirements.txt
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python -m django --version 2^>^&1') do set DJANGO_VERSION=%%i
echo %GREEN%[OK]%RESET% Django %DJANGO_VERSION% found
echo.

REM ??? Backend
echo %YELLOW%[STARTING]%RESET% Starting Django Backend...
echo.
start "Khalifa Pharmacy - Django Backend [Port 8000]" cmd /k "cd /d "%SYSTEM_DIR%" && echo %GREEN%[SUCCESS]%RESET% Django Backend started on http://0.0.0.0:8000 && echo. && python manage.py runserver 0.0.0.0:8000"
timeout /t 3 /nobreak >nul
echo %GREEN%[OK]%RESET% Django Backend window opened (Port 8000)
echo.

REM ??? WPPConnect Server
echo %YELLOW%[STARTING]%RESET% Starting WPPConnect Server...
echo.
start "Khalifa Pharmacy - WPPConnect Server [Port 3000]" cmd /k "cd /d "%WPPCONNECT_DIR%" && echo %GREEN%[SUCCESS]%RESET% WPPConnect Server started on http://localhost:3000 && echo. && npm start"
timeout /t 2 /nobreak >nul
echo %GREEN%[OK]%RESET% WPPConnect Server window opened (Port 3000)
echo.

REM ??????? ???????
echo ============================================
echo %GREEN%[SUCCESS]%RESET% Both services started successfully!
echo.
echo ?? Access Points:
echo   ? Django Admin:     http://localhost:8000/admin/
echo   ? Django Frontend:  http://localhost:8000/login/
echo   ? WPPConnect API:   http://localhost:3000/
echo   ? WPPConnect QR:    http://localhost:3000/qr-code
echo.
echo ?? Default Credentials:
echo   ? Admin:    admin / admin123
echo   ? Agent:    agent1 / agent123
echo.
echo ?? To stop all services:
echo   ? Run: stop.bat
echo   ? Or press CTRL+C in both terminal windows
echo.
echo ============================================
echo.

endlocal
pause
