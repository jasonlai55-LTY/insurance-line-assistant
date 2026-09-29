import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

SQLITE_URL = "sqlite+aiosqlite:///./local_dev.db"

# 預設本地無 PostgreSQL 容器時預設切換為 SQLite 零組態資料庫
if os.environ.get("USE_SQLITE") == "1" or not settings.POSTGRES_SERVER:
    engine = create_async_engine(SQLITE_URL, echo=False, future=True)
else:
    engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True, pool_pre_ping=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


def switch_to_sqlite():
    global engine, AsyncSessionLocal
    engine = create_async_engine(SQLITE_URL, echo=False, future=True)
    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    return engine


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
