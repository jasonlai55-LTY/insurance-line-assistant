import subprocess
import time
import os
import sys
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("==================================================================", flush=True)
print("[保險業務 LINE 助手] 對外網路隧道啟動工具 (Cloudflare & ngrok)", flush=True)
print("==================================================================", flush=True)

# 1. 強制關閉舊的隧道進程
os.system("taskkill /f /im cloudflared.exe >nul 2>&1")
os.system("taskkill /f /im ngrok.exe >nul 2>&1")
time.sleep(2)

STATIC_DOMAIN = "monetary-concur-showcase.ngrok-free.dev"

# 2. 啟動 Cloudflare 零警告對外隧道 (帶 --http-host-header localhost 確保穩定)
print("\n[1/2] 正在啟動 Cloudflare 零警告對外隧道 (http://127.0.0.1:3000)...", flush=True)
cf_proc = subprocess.Popen(
    [".\\cloudflared.exe", "tunnel", "--url", "http://127.0.0.1:3000", "--http-host-header", "localhost"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    encoding="utf-8",
    errors="ignore"
)

cf_url = ""
start_time = time.time()
while (time.time() - start_time < 10):
    line = cf_proc.stdout.readline() if cf_proc.stdout else ""
    if "trycloudflare.com" in line:
        match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
        if match:
            cf_url = match.group(0)
            break

# 3. 啟動 ngrok 固定網址隧道
print(f"\n[2/2] 正在啟動 ngrok 固定域名隧道 -> {STATIC_DOMAIN}...", flush=True)
ngrok_proc = subprocess.Popen(
    [".\\ngrok.exe", "http", f"--url={STATIC_DOMAIN}", "http://127.0.0.1:3000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    encoding="utf-8",
    errors="ignore"
)

time.sleep(2)

print("\n==================================================================", flush=True)
print("恭喜！對外連線隧道已全部上線：", flush=True)
print("==================================================================", flush=True)
if cf_url:
    print("[推薦] Cloudflare 免費直連網址（無警告、不擋連線）：", flush=True)
    print(f"   -> {cf_url}", flush=True)
    print("------------------------------------------------------------------", flush=True)
print(f"ngrok 固定網址：", flush=True)
print(f"   -> https://{STATIC_DOMAIN}", flush=True)
print("==================================================================", flush=True)
print("\n提示：請勿關閉此視窗。測試完畢按下 Ctrl+C 即可結束服務。")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    cf_proc.terminate()
    ngrok_proc.terminate()
    print("所有隧道已停止服務。")
