from typing import List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.core.database import get_db
from app.core.security import verify_token
from app.db.models import Agent, NotificationLog
from app.schemas.notification import NotificationLogResponse

router = APIRouter(prefix="/notifications", tags=["Notification Center"])


async def get_current_agent_or_default(authorization: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)) -> Agent:
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        agent_code = verify_token(token)
        if agent_code and not agent_code.startswith("admin:"):
            result = await db.execute(select(Agent).where(Agent.agent_code == agent_code, Agent.status == "active"))
            agent = result.scalar_one_or_none()
            if agent:
                return agent
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="帳號已被解綁、離職或從主檔移除")

    result = await db.execute(select(Agent).where(Agent.agent_code == "A001", Agent.status == "active"))
    agent = result.scalar_one_or_none()
    if agent:
        return agent
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到預設業務員資料")


@router.get("/my-logs", response_model=List[NotificationLogResponse])
async def get_my_notification_logs(
    category: Optional[str] = None,
    unread_only: bool = Query(False, description="僅顯示未讀通知"),
    limit: int = Query(20, ge=1, le=100, description="分頁比數限制 (預設最新 20 筆)"),
    offset: int = Query(0, ge=0),
    agent: Agent = Depends(get_current_agent_or_default),
    db: AsyncSession = Depends(get_db)
):
    """
    業務員查詢個人歷史通知紀錄
    - 支援分頁與最新 20 筆限制 (避免無限累積影響 UX)
    - 支援未讀篩選與分類過濾
    """
    stmt = select(NotificationLog).where(NotificationLog.agent_id == agent.id)
    if category:
        stmt = stmt.where(NotificationLog.category == category)
    if unread_only:
        stmt = stmt.where(NotificationLog.is_read == False)

    stmt = stmt.order_by(NotificationLog.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.put("/mark-all-read")
async def mark_all_logs_as_read(
    agent: Agent = Depends(get_current_agent_or_default),
    db: AsyncSession = Depends(get_db)
):
    """一鍵全部標記為已讀 (降低業務員清理負擔)"""
    await db.execute(
        update(NotificationLog)
        .where(NotificationLog.agent_id == agent.id, NotificationLog.is_read == False)
        .values(is_read=True)
    )
    await db.commit()
    return {"status": "success", "message": "已全部標記為已讀"}


@router.put("/logs/{log_id}/read")
async def mark_log_as_read(
    log_id: str,
    agent: Agent = Depends(get_current_agent_or_default),
    db: AsyncSession = Depends(get_db)
):
    """單筆標記通知為已讀"""
    await db.execute(
        update(NotificationLog)
        .where(NotificationLog.id == log_id, NotificationLog.agent_id == agent.id)
        .values(is_read=True)
    )
    await db.commit()
    return {"status": "success", "message": "已更新為已讀狀態"}


@router.delete("/logs/{log_id}")
async def delete_notification_log(
    log_id: str,
    agent: Agent = Depends(get_current_agent_or_default),
    db: AsyncSession = Depends(get_db)
):
    """業務員手動移除/刪除單筆歷史通知"""
    await db.execute(
        delete(NotificationLog)
        .where(NotificationLog.id == log_id, NotificationLog.agent_id == agent.id)
    )
    await db.commit()
    return {"status": "success", "message": "通知已成功移除"}
