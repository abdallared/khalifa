@echo off
echo ============================================================
echo STARTING WPPCONNECT AND DJANGO SERVERS (USING VENV)
echo ============================================================
echo.

echo Activating Virtual Environment...
echo.
cd System
call venv\Scripts\activate.bat
cd ..

echo.
echo Starting WPPConnect Server...
echo.
cd wppconnect-server
start "WPPConnect Server" cmd /k "node server.js"

timeout /t 5 /nobreak > nul

echo.
echo Starting Django Server (using venv)...
echo.
cd ..\System
start "Django Server (venv)" cmd /k "call venv\Scripts\activate.bat && python manage.py runserver 0.0.0.0:8000"

timeout /t 3 /nobreak > nul

echo.
echo ============================================================
echo SERVERS STARTED WITH VIRTUAL ENVIRONMENT!
echo ============================================================
echo.
echo WPPConnect Server: http://localhost:3000
echo Django Server:     http://localhost:8000
echo.
echo Virtual Environment: System\venv
echo Python Version:      3.14.0
echo.
echo Close this window after verifying servers are running.
echo.
pause
