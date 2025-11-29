@echo off
echo ============================================================
echo STARTING WPPCONNECT AND DJANGO SERVERS
echo ============================================================
echo.

echo Starting WPPConnect Server...
echo.
cd wppconnect-server
start "WPPConnect Server" cmd /k "node server.js"

timeout /t 5 /nobreak > nul

echo.
echo Starting Django Server...
echo.
cd ..\System
start "Django Server" cmd /k "python manage.py runserver 0.0.0.0:8000"

timeout /t 3 /nobreak > nul

echo.
echo ============================================================
echo SERVERS STARTED!
echo ============================================================
echo.
echo WPPConnect Server: http://localhost:3000
echo Django Server:     http://localhost:8000
echo.
echo Close this window after verifying servers are running.
echo.
pause
