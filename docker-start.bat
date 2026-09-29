@echo off
chcp 65001 >nul
echo ===================================================
echo 🚀 正在啟動 [保險業務 LINE 助手] 全套 Docker 容器服務...
echo ===================================================

echo [1/3] 開始編譯與建立 Docker 鏡像 (Build Docker Images)...
docker compose build

if %ERRORLEVEL% NEQ 0 (
    echo [錯誤] Docker 編譯失敗！請確認 Docker Desktop 是否已啟動。
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/3] 正在背景啟動容器 (Postgres, Redis, Backend, LIFF, Admin CMS)...
docker compose up -d

echo.
echo [3/3] 檢查容器運行狀態...
docker compose ps

echo.
echo ===================================================
echo 🎉 保險業務 LINE 助手 Docker 服務啟動完成！
echo ===================================================
echo  - FastAPI 後端 API : http://localhost:8000/docs
echo  - LIFF 前檯 App   : http://localhost:3000
echo  - Admin CMS 後臺  : http://localhost:3001
echo  - PostgreSQL 資料庫: localhost:5432
echo  - Redis 快取      : localhost:6379
echo ===================================================
pause
