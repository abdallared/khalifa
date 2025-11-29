@echo off
REM ============================================
REM Stop Script for Khalifa Pharmacy System
REM ?? ????? ???? ??????? ?????
REM ============================================
REM Stop.bat - ?????? Django Backend ? WPPConnect Server

setlocal enabledelayedexpansion

REM ?????
set "GREEN=[92m"
set "BLUE=[94m"
set "YELLOW=[93m"
set "RED=[91m"
set "RESET=[0m"

cls
echo.
echo ============================================
echo   ???? ??????? ????? - ?? ???????
echo   Khalifa Pharmacy System - Stop Script
echo ============================================
echo.

echo %YELLOW%[STOPPING]%RESET% Stopping all services...
echo.

REM ????? Django Backend (Python)
echo %YELLOW%[KILLING]%RESET% Stopping Django Backend (python.exe)...
taskkill /IM python.exe /F >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%[OK]%RESET% Django Backend stopped
) else (
    echo %BLUE%[INFO]%RESET% Django Backend was not running
)

REM ?????? ????
timeout /t 1 /nobreak >nul

REM ????? WPPConnect Server (Node.js)
echo %YELLOW%[KILLING]%RESET% Stopping WPPConnect Server (node.exe)...
taskkill /IM node.exe /F >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%[OK]%RESET% WPPConnect Server stopped
) else (
    echo %BLUE%[INFO]%RESET% WPPConnect Server was not running
)

REM ?????? ????
timeout /t 1 /nobreak >nul

REM ?????? ?? ????? ????????
echo.
echo %YELLOW%[VERIFYING]%RESET% Verifying services are stopped...
echo.

tasklist /FI "IMAGENAME eq python.exe" 2>nul | find /I "python.exe" >nul
if %errorlevel% neq 0 (
    echo %GREEN%[VERIFIED]%RESET% Python processes stopped
) else (
    echo %RED%[WARNING]%RESET% Some Python processes still running
    echo Attempting force kill...
    taskkill /IM python.exe /F /T >nul 2>&1
)

tasklist /FI "IMAGENAME eq node.exe" 2>nul | find /I "node.exe" >nul
if %errorlevel% neq 0 (
    echo %GREEN%[VERIFIED]%RESET% Node.js processes stopped
) else (
    echo %RED%[WARNING]%RESET% Some Node.js processes still running
    echo Attempting force kill...
    taskkill /IM node.exe /F /T >nul 2>&1
)

echo.
echo ============================================
echo %GREEN%[SUCCESS]%RESET% All services stopped successfully!
echo.
echo ?? Stopped Services:
echo   ? Django Backend (Port 8000)
echo   ? WPPConnect Server (Port 3000)
echo.
echo ?? To start again:
echo   ? Run: run.bat
echo.
echo ============================================
echo.

REM ????? ??? 3 ?????
timeout /t 3 /nobreak

endlocal
