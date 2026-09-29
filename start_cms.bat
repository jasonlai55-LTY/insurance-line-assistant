@echo off
echo Installing dependencies and launching Admin CMS...
cd /d "%~dp0admin-cms"
if not exist node_modules (
    call npm install
)
call npm run dev -- --port 3001
pause
