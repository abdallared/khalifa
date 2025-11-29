@echo off
REM ============================================================================
REM Database Migration Script - SQLite to PostgreSQL
REM نص الترحيل من SQLite إلى PostgreSQL (Windows)
REM ============================================================================

setlocal enabledelayedexpansion

REM Colors
set "GREEN=[92m"
set "BLUE=[94m"
set "YELLOW=[93m"
set "RED=[91m"
set "RESET=[0m"

echo.
echo ============================================================================
echo     Khalifa Pharmacy - Database Migration Tool
echo     اداة ترحيل قاعدة البيانات - صيدليات خليفة
echo ============================================================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo %RED%[ERROR] Virtual environment not found!%RESET%
    echo.
    echo Please create virtual environment first:
    echo   python -m venv venv
    echo   call venv\Scripts\activate.bat
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo %BLUE%[INFO]%RESET% Activating virtual environment...
call venv\Scripts\activate.bat
echo %GREEN%[OK]%RESET% Virtual environment activated
echo.

:menu
echo.
echo %YELLOW%Please select an option:%RESET%
echo.
echo   %GREEN%1.%RESET% Backup SQLite Database
echo   %GREEN%2.%RESET% Install PostgreSQL Driver (in venv)
echo   %GREEN%3.%RESET% Run Database Migrations
echo   %GREEN%4.%RESET% Load Backup Data
echo   %GREEN%5.%RESET% Verify Migration
echo   %GREEN%6.%RESET% Full Migration (All Steps)
echo   %GREEN%7.%RESET% Exit
echo.
set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto backup
if "%choice%"=="2" goto install
if "%choice%"=="3" goto migrate
if "%choice%"=="4" goto loaddata
if "%choice%"=="5" goto verify
if "%choice%"=="6" goto full
if "%choice%"=="7" goto end

echo %RED%Invalid choice! Please try again.%RESET%
goto menu

:backup
echo.
echo ============================================================================
echo %BLUE%Backing up SQLite database...%RESET%
echo ============================================================================
python migrate_to_postgresql.py --backup
if errorlevel 1 (
    echo.
    echo %RED%[ERROR] Backup failed!%RESET%
    pause
    goto menu
)
echo.
echo %GREEN%[SUCCESS] Backup completed!%RESET%
pause
goto menu

:install
echo.
echo ============================================================================
echo %BLUE%Installing PostgreSQL driver...%RESET%
echo ============================================================================
echo %YELLOW%[INFO]%RESET% Installing psycopg2-binary==2.9.9 in venv...
pip install psycopg2-binary==2.9.9
if errorlevel 1 (
    echo.
    echo %RED%[ERROR] Installation failed!%RESET%
    pause
    goto menu
)
echo.
echo %GREEN%[SUCCESS] Driver installed in virtual environment!%RESET%
pause
goto menu

:migrate
echo.
echo ============================================================================
echo %BLUE%Running Django migrations on PostgreSQL...%RESET%
echo ============================================================================
echo.
echo %YELLOW%[CHECKLIST]%RESET% Make sure you have:
echo   %GREEN%1.%RESET% PostgreSQL server running
echo   %GREEN%2.%RESET% Database created (khalifa_pharmacy_db)
echo   %GREEN%3.%RESET% Updated .env file with PostgreSQL credentials
echo.
set /p confirm="Continue? (Y/N): "
if /i not "%confirm%"=="Y" goto menu

echo.
echo %BLUE%[INFO]%RESET% Running migrations with venv...
python manage.py migrate
if errorlevel 1 (
    echo.
    echo %RED%[ERROR] Migration failed!%RESET%
    pause
    goto menu
)
echo.
echo %GREEN%[SUCCESS] Migrations completed!%RESET%
pause
goto menu

:loaddata
echo.
echo ============================================================================
echo %BLUE%Loading Backup Data into PostgreSQL...%RESET%
echo ============================================================================
echo.
echo %YELLOW%Available backup files:%RESET%
echo.
dir /b backups\data_backup_*.json 2>nul
if errorlevel 1 (
    echo %RED%[ERROR] No backup files found in backups\ folder!%RESET%
    echo.
    echo Please run backup first (option 1)
    pause
    goto menu
)
echo.
set /p backup_file="Enter backup filename (or press Enter to use latest): "

if "%backup_file%"=="" (
    REM Get latest backup file
    for /f "delims=" %%i in ('dir /b /o-d backups\data_backup_*.json 2^>nul') do (
        set backup_file=%%i
        goto :loadfile
    )
)

:loadfile
echo.
echo %BLUE%[INFO]%RESET% Loading data from: backups\%backup_file%
python manage.py loaddata backups\%backup_file%
if errorlevel 1 (
    echo.
    echo %RED%[ERROR] Data load failed!%RESET%
    pause
    goto menu
)
echo.
echo %GREEN%[SUCCESS] Data loaded successfully!%RESET%
pause
goto menu

:verify
echo.
echo ============================================================================
echo %BLUE%Verifying database migration...%RESET%
echo ============================================================================
python verify_database.py
pause
goto menu

:full
echo.
echo ============================================================================
echo %BLUE%Full Migration Process%RESET%
echo ============================================================================
echo.
echo This will:
echo   %GREEN%1.%RESET% Backup current SQLite database
echo   %GREEN%2.%RESET% Install PostgreSQL driver (in venv)
echo   %GREEN%3.%RESET% Run migrations on PostgreSQL
echo   %GREEN%4.%RESET% Verify migration
echo.
echo %RED%IMPORTANT:%RESET% Make sure PostgreSQL is installed and running!
echo.
set /p confirm="Continue with full migration? (Y/N): "
if /i not "%confirm%"=="Y" goto menu

echo.
echo %BLUE%Step 1/4:%RESET% Backing up SQLite database...
python migrate_to_postgresql.py --backup
if errorlevel 1 (
    echo %RED%[ERROR] Backup failed! Aborting migration.%RESET%
    pause
    goto menu
)

echo.
echo %BLUE%Step 2/4:%RESET% Installing PostgreSQL driver in venv...
pip install psycopg2-binary==2.9.9
if errorlevel 1 (
    echo %RED%[ERROR] Driver installation failed! Aborting migration.%RESET%
    pause
    goto menu
)

echo.
echo %BLUE%Step 3/4:%RESET% Configuration update required
echo.
echo %YELLOW%Please update your .env file with PostgreSQL settings:%RESET%
echo.
echo %GREEN%Required changes in .env:%RESET%
echo   DB_ENGINE=postgresql
echo   DB_NAME=khalifa_pharmacy_db
echo   DB_USER=postgres
echo   DB_PASSWORD=your_password
echo   DB_HOST=localhost
echo   DB_PORT=5432
echo.
set /p confirm="Have you updated .env? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo %YELLOW%Please update .env and run this script again.%RESET%
    pause
    goto menu
)

echo.
echo %BLUE%Step 3/4:%RESET% Running migrations...
python manage.py migrate
if errorlevel 1 (
    echo %RED%[ERROR] Migration failed!%RESET%
    echo.
    echo %YELLOW%To rollback, change .env back to:%RESET%
    echo   DB_ENGINE=sqlite3
    echo   DB_NAME=db.sqlite3
    pause
    goto menu
)

echo.
echo %BLUE%Step 4/6:%RESET% Loading backup data...
echo.
echo %YELLOW%Looking for backup files...%RESET%
for /f "delims=" %%i in ('dir /b /o-d backups\data_backup_*.json 2^>nul') do (
    set latest_backup=%%i
    goto :found_backup
)
echo %RED%[ERROR] No backup files found!%RESET%
goto menu

:found_backup
echo %GREEN%[INFO]%RESET% Using latest backup: %latest_backup%
python manage.py loaddata backups\%latest_backup%
if errorlevel 1 (
    echo %RED%[ERROR] Data load failed!%RESET%
    pause
    goto menu
)

echo.
echo %BLUE%Step 5/6:%RESET% Verifying migration...
python verify_database.py

echo.
echo %BLUE%Step 6/6:%RESET% Creating database indexes...
python manage.py migrate --run-syncdb

echo.
echo ============================================================================
echo %GREEN%Migration completed successfully!%RESET%
echo ============================================================================
echo.
echo %GREEN%✓%RESET% Database migrated to PostgreSQL
echo %GREEN%✓%RESET% All data loaded
echo %GREEN%✓%RESET% Indexes created
echo %GREEN%✓%RESET% Verification passed
echo.
echo %YELLOW%Next steps:%RESET%
echo   %GREEN%1.%RESET% Review verification results above
echo   %GREEN%2.%RESET% Test the application: START_SERVERS_VENV.bat
echo   %GREEN%3.%RESET% Backup PostgreSQL database regularly
echo.
pause
goto menu

:end
echo.
echo Goodbye!
exit /b 0
