# 保險業務 LINE 助手系統 (Insurance LINE Assistant)

結合 **LINE 官方帳號 (OA) + LIFF 輕應用 + 通路管理後台 (CMS) + 後端 Webhook & Core API** 的全方位保險業務賦能平台。

## 專案架構 (Monorepo)

- `backend/`: FastAPI + PostgreSQL + SQLAlchemy 2.0 (Async) + Alembic + Redis + LINE Bot SDK
- `liff-frontend/`: Vue 3 + Vite + Tailwind CSS + `@line/liff` SDK (業務員端輕應用)
- `admin-cms/`: Vue 3 + Vite + Tailwind CSS + Element Plus (通路管理後台)

## 核心功能與資安規範

1. **LINE Webhook & 關鍵字查詢**：提供 Flex Message 卡片回傳商品與行政規範。
2. **業務員身份驗證**：工號 + 簡訊 OTP 雙重驗證與 LINE User ID 綁定。
3. **資安個資脫敏**：行政照會與個人通知強制遮蔽客戶姓名、身分證字號與保單號碼。
4. **內部文件防護**：核保與銷售手冊僅限驗證業務員存取。
5. **CMS 批次推播引擎**：支援 Excel 匯入、防呆校驗與分眾標籤推播。

## 快速啟動 (Docker Compose)

```bash
docker-compose up --build -d
```

- 後端 API (FastAPI Swagger UI): `http://localhost:8000/docs`
- 業務員端 LIFF App: `http://localhost:3000`
- 通路管理後台 CMS: `http://localhost:3001`
