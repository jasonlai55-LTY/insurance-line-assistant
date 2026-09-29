@echo off
echo Starting Insurance LINE Assistant Complete System...
cd /d "%~dp0"

start "FastAPI Backend (8000)" cmd /k "start_backend.bat"
start "LIFF Mobile App (3000)" cmd /k "start_liff.bat"
start "Admin CMS (3001)" cmd /k "start_cms.bat"

echo.
echo ======================================================================
echo System started successfully!
echo Backend API (Swagger UI): http://localhost:8000/docs
echo LIFF Mobile App:         http://localhost:3000
echo Admin CMS:                http://localhost:3001
echo ======================================================================
pause
