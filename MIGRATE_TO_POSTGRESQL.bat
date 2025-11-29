@echo off
REM ============================================================================
REM Quick Launch - Database Migration Tool
REM أداة الترحيل السريعة - قاعدة البيانات
REM ============================================================================
REM Launches the migration tool from project root
REM ============================================================================

setlocal

REM Colors
set "GREEN=[92m"
set "BLUE=[94m"
set "YELLOW=[93m"
set "RED=[91m"
set "RESET=[0m"

cls
echo.
echo ============================================================================
echo   %BLUE%Khalifa Pharmacy - PostgreSQL Migration%RESET%
echo   %BLUE%صيدليات خليفة - الترحيل إلى PostgreSQL%RESET%
echo ============================================================================
echo.

REM Check if System directory exists
if not exist "System" (
    echo %RED%[ERROR] System directory not found!%RESET%
    echo Please run this script from the project root directory.
    pause
    exit /b 1
)

REM Check if venv exists
if not exist "System\venv" (
    echo %RED%[ERROR] Virtual environment not found!%RESET%
    echo.
    echo Please create virtual environment first:
    echo   cd System
    echo   python -m venv venv
    echo   call venv\Scripts\activate.bat
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo %BLUE%[INFO]%RESET% Launching migration tool...
echo %BLUE%[INFO]%RESET% Virtual environment: System\venv
echo.

cd System
call migrate.bat

cd ..
endlocal
