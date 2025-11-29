@echo off
REM ============================================
REM Development Mode Script for Khalifa Pharmacy
REM ?? ??? ??????? ????? ??????? ?????
REM ============================================
REM Dev.bat - ?????? ???????? ?? ??? ???????

setlocal enabledelayedexpansion

set ROOT_DIR=%~dp0
set SYSTEM_DIR=%ROOT_DIR%System
set WPPCONNECT_DIR=%ROOT_DIR%wppconnect-server

set "GREEN=[92m"
set "BLUE=[94m"
set "YELLOW=[93m"
set "RED=[91m"
set "RESET=[0m"

cls
echo.
echo ============================================
echo   ???? ??????? ????? - ??? ???????
echo   Khalifa Pharmacy - Development Mode
echo ============================================
echo.

echo %YELLOW%[INFO]%RESET% Development Mode:
echo   ? Django: Auto-reload on code changes
echo   ? WPPConnect: Auto-restart with nodemon
echo.

REM ??? Backend ?? ??? ???????
echo %YELLOW%[STARTING]%RESET% Starting Django Backend (Development Mode)...
echo.
start "Khalifa Pharmacy - Django Dev [Port 8000]" cmd /k "cd /d "%SYSTEM_DIR%" && echo %GREEN%[SUCCESS]%RESET% Django running with auto-reload && python manage.py runserver 0.0.0.0:8000"
timeout /t 3 /nobreak >nul
echo %GREEN%[OK]%RESET% Django Backend window opened
echo.

REM ??? WPPConnect Server ?? ??? ???????
echo %YELLOW%[STARTING]%RESET% Starting WPPConnect Server (Development Mode with nodemon)...
echo.
start "Khalifa Pharmacy - WPPConnect Dev [Port 3000]" cmd /k "cd /d "%WPPCONNECT_DIR%" && echo %GREEN%[SUCCESS]%RESET% WPPConnect running with auto-restart && npm run dev"
timeout /t 2 /nobreak >nul
echo %GREEN%[OK]%RESET% WPPConnect Server window opened
echo.

REM ??? Delay Tracker
echo %YELLOW%[STARTING]%RESET% Starting Delay Tracker (Auto-checks every 1 minute)...
echo.
start "Khalifa Pharmacy - Delay Tracker" cmd /k "cd /d "%SYSTEM_DIR%" && echo %GREEN%[SUCCESS]%RESET% Delay Tracker running - Monitoring ticket delays && python run_delay_tracker.py"
timeout /t 2 /nobreak >nul
echo %GREEN%[OK]%RESET% Delay Tracker window opened
echo.

echo ============================================
echo %GREEN%[SUCCESS]%RESET% Development mode started!
echo.
echo ?? Auto-reload enabled:
echo   ? Django: Watches for Python file changes
echo   ? WPPConnect: Watches for JS/JSON changes
echo   ? Delay Tracker: Checks every 1 minute
echo.
echo ?? Access Points:
echo   ? Django:       http://localhost:8000/login/
echo   ? WPPConnect:   http://localhost:3000/qr-code
echo.
echo ?? To stop:
echo   ? Run: stop.bat
echo   ? Press CTRL+C in terminal windows
echo.
echo ============================================
echo.

endlocal
pause
