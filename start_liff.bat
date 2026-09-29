@echo off
echo Installing dependencies and launching LIFF Mobile Frontend...
cd /d "%~dp0liff-frontend"
if not exist node_modules (
    call npm install
)
call npm run dev -- --port 3000
pause
