# 🛡️ 保險業務員 LINE 助手 — IT 開發者交接與技術部署指南 (IT Handoff Guide)

> **致 IT/工程團隊**：
> 本專案為已完成開發並通過測試之 production-ready MVP 雛形。採用標準現代化全端架構（FastAPI + Vue 3 + Docker），**無需從零開發**，可以直接 100% 移植、部署與接手維護。

---

## 📐 1. 系統技術棧 (Tech Stack)

- **後端 API**：Python 3.10+ / FastAPI / SQLAlchemy (Async) / Pydantic v2
- **資料庫**：SQLite (預設測試/備援) / PostgreSQL (生產環境)
- **管理後台**：Vue 3 (Composition API) / Vite / Tailwind CSS / Element Plus
- **業務員端 (LIFF)**：Vue 3 / Vite / Tailwind CSS / LINE LIFF SDK v2
- **對外通道/部署**：Docker / Docker Compose / Nginx / Cloudflare Tunnel / ngrok

---

## 📁 2. 專案目錄結構 (Project Structure)

```text
insurance-line-assistant/
├── backend/                  # FastAPI 後端 API 服務
│   ├── app/
│   │   ├── api/v1/           # RESTful API 路由 (admin, products, notifications, auth, webhook)
│   │   ├── core/             # 核心配置、資料庫連線 (database.py), 資安 (security.py)
│   │   ├── db/               # SQLAlchemy 模型 (models.py)
│   │   ├── schemas/          # Pydantic 數據校驗模型
│   │   └── services/         # 業務邏輯層 (excel_service, asset_service, line_service)
│   ├── requirements.txt      # Python 依賴包清單
│   └── venv/                 # 虛擬環境
├── admin-cms/                # Vue 3 管理後台 (Port 3001)
│   ├── src/
│   │   ├── views/            # AgentManagement, AssetManagement, TagManagement, BatchPush
│   │   └── App.vue
├── liff-frontend/            # Vue 3 LINE LIFF 業務員端 (Port 3000)
│   ├── src/
│   │   ├── views/            # Home, Products, Guidelines, Notifications
│   │   └── App.vue
├── start_all_services.ps1    # PowerShell 一鍵啟動腳本
├── start_all_services.bat    # Windows 啟動批次檔
└── start_tunnels.py          # 對外網路隧道自動化管理工具
```

---

## 🚀 3. 部署與資料庫切換指南 (Production Deployment)

### 3.1 切換至 PostgreSQL
後端原生支援 `PostgreSQL`，只需在 `backend/.env` 替換環境變數：
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/insurance_db
```
系統在啟動時會自動執行 `Base.metadata.create_all` 建立所有 Tables（`agents`, `product_assets`, `categories`, `notification_logs`, `admin_users`），無須手動下 DDL。

### 3.2 啟動後端 API
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- **Swagger 互動式 API 文件**：`http://localhost:8000/docs`
- **ReDoc 文件**：`http://localhost:8000/redoc`

### 3.3 啟動前端 (Vite)
```bash
# Admin CMS
cd admin-cms && npm install && npm run dev -- --port 3001

# LIFF Frontend
cd liff-frontend && npm install && npm run dev -- --port 3000
```

---

## 🔒 4. 關鍵資安與架構設計說明 (Security Architecture)

1. **解耦架構 (Decoupled Architecture)**：
   本系統不直接外連公司 Core System DB，所有照會與主檔異動皆透過 Excel 批次傳輸，零核心系統滲透風險。
2. **自動個資脫敏 (Data Masking)**：
   照會內容發送前與資料庫紀錄皆在 `backend/app/services/excel_service.py` 執行去識別化處理（身分證字號 A123***789、手機號碼 0912***678）。
3. **分級授權 (RBAC & OTP)**：
   內部限閱文件與特批條款僅限 `Agent.is_verified == True` 之驗證業務員讀取。

---

## 💬 5. IT 接手 FAQ

- **Q: 是否需要重頭開發？**
  - **不需要**。專案為完整 RESTful API + Vue 3 全端程式碼，IT 工程師可直接在基礎上擴充。
- **Q: 如何修改 API 或擴充欄位？**
  - 後端欄位定義於 `backend/app/db/models.py`，API 路由於 `backend/app/api/v1/`，遵循標準 FastAPI 規範，擴充極為簡單。
