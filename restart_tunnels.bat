@echo off
chcp 65001 >nul
echo 正在啟動/重連 ngrok 永久靜態網址隧道...
python start_tunnels.py
pause
