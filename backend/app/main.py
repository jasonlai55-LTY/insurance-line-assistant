from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core import database
from app.api.v1.router import api_router
from app.db.models import Agent, Category, ProductAsset, AdminUser
from app.core.security import get_password_hash
from sqlalchemy import select, text

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


async def seed_initial_data():
    async with database.AsyncSessionLocal() as session:
        # 建立預設測試業務員 A001
        res = await session.execute(select(Agent).where(Agent.agent_code == "A001"))
        if not res.scalar_one_or_none():
            agent = Agent(
                agent_code="A001",
                name="張大明",
                phone="0912345678",
                channel="直營",
                branch_office="台北一處",
                job_title="區經理",
                is_verified=False
            )
            session.add(agent)

        # 建立預設通知分類 (notification_category)
        default_notif_cats = [
            ("行政照會", 1),
            ("商品異動", 2),
            ("營運活動", 3)
        ]
        for cat_name, order in default_notif_cats:
            c_res = await session.execute(select(Category).where(Category.type == "notification_category", Category.name == cat_name))
            if not c_res.scalar_one_or_none():
                session.add(Category(type="notification_category", name=cat_name, sort_order=order))

        # 建立預設行政規範分類 (admin_rule)
        default_rule_cats = [
            ("投保規則", 1),
            ("保費規則", 2),
            ("保全規則", 3),
            ("理賠注意事項", 4),
            ("各式表單", 5)
        ]
        for cat_name, order in default_rule_cats:
            c_res = await session.execute(select(Category).where(Category.type == "admin_rule", Category.name == cat_name))
            if not c_res.scalar_one_or_none():
                session.add(Category(type="admin_rule", name=cat_name, sort_order=order))

        # 建立預設測試素材分類
        cat_res = await session.execute(select(Category).where(Category.name == "銷售手冊"))
        cat = cat_res.scalar_one_or_none()
        if not cat:
            cat = Category(type="product_asset", name="銷售手冊", sort_order=1)
            session.add(cat)
            await session.flush()

        # 建立預設商品 ACC01
        asset_res = await session.execute(select(ProductAsset).where(ProductAsset.product_code == "ACC01"))
        if not asset_res.scalar_one_or_none():
            asset = ProductAsset(
                type="product",
                product_code="ACC01",
                title="新意外險專案銷售手冊",
                category_id=cat.id,
                file_url="https://example.com/ACC01_manual.pdf",
                description="2026 最新版意外險費率與理賠說明手冊",
                is_internal_only=False,
                status="published"
            )
            session.add(asset)

        # 建立預設管理者 admin
        admin_res = await session.execute(select(AdminUser).where(AdminUser.username == "admin"))
        if not admin_res.scalar_one_or_none():
            admin = AdminUser(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                role="admin"
            )
            session.add(admin)

        await session.commit()


@app.on_event("startup")
async def startup_event():
    try:
        async with database.engine.begin() as conn:
            await conn.run_sync(database.Base.metadata.create_all)
        print("Connected to PostgreSQL successfully.")
        await seed_initial_data()
    except Exception as e:
        print("----------------------------------------------------------------------")
        print("PostgreSQL 連線未就緒，自動切換至本地 SQLite 零組態備援資料庫。")
        active_engine = database.switch_to_sqlite()
        async with active_engine.begin() as conn:
            await conn.run_sync(database.Base.metadata.create_all)
            # 自動補新增之欄位 (防呆 SQLite 資料庫結構微調)
            try:
                await conn.execute(text("ALTER TABLE notification_logs ADD COLUMN raw_content TEXT"))
            except Exception:
                pass
            try:
                await conn.execute(text("ALTER TABLE agents ADD COLUMN district VARCHAR(100)"))
            except Exception:
                pass
        await seed_initial_data()
        print("SQLite 備援資料庫與預設測試資料 (A001 / 0912345678) 初始化完成！")
        print("----------------------------------------------------------------------")


@app.get("/health")
async def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}
