$root = $PSScriptRoot

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "    Starting Insurance Line Assistant Services...   " -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

Write-Host "[1/4] Starting FastAPI Backend (Port 8000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$root\backend'; .\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`""

Start-Sleep -Seconds 3

Write-Host "[2/4] Starting LIFF Frontend (Port 3000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$root\liff-frontend'; npm run dev`""

Start-Sleep -Seconds 3

Write-Host "[3/4] Starting Admin CMS (Port 3001)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$root\admin-cms'; npm run dev`""

Start-Sleep -Seconds 4

Write-Host "[4/4] Starting Cloudflare & ngrok Tunnel Daemon..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$root'; .\backend\venv\Scripts\python.exe start_tunnels.py`""

Write-Host "===================================================" -ForegroundColor Yellow
Write-Host "   All Services Launched Successfully!" -ForegroundColor Yellow
Write-Host "   - Admin CMS:   http://localhost:3001" -ForegroundColor White
Write-Host "   - LIFF Mobile: http://localhost:3000" -ForegroundColor White
Write-Host "   - Backend API: http://localhost:8000/docs" -ForegroundColor White
Write-Host "===================================================" -ForegroundColor Yellow
