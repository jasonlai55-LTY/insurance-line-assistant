from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.core.database import get_db
from app.db.models import Agent, Notification, NotificationLog
from app.services.excel_service import ExcelNotificationImportService
from app.services.masking_service import DataMaskingService
from app.services.line_service import LineFlexBuilder, LineMessagingService
from app.schemas.notification import BatchPushRequest
from pydantic import BaseModel
from datetime import datetime, timezone

router = APIRouter(prefix="/admin/notifications", tags=["CMS Notification Engine"])


@router.post("/parse-excel")
async def parse_and_validate_excel(file: UploadFile = File(...)):
    """
    CMS 匯入 Excel 預覽與防呆校驗點
    - 上傳檔名校驗
    - 欄位格式檢查
    - 自動脫敏預覽
    """
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="僅支援 .xlsx 或 .xls 格式之 Excel 檔案")

    content = await file.read()
    valid_items, errors = ExcelNotificationImportService.process_excel_bytes(content)

    return {
        "filename": file.filename,
        "total_rows_parsed": len(valid_items) + len(errors),
        "valid_count": len(valid_items),
        "error_count": len(errors),
        "valid_items": valid_items,
        "errors": errors
    }


@router.post("/execute-batch-push")
async def execute_batch_push(payload: BatchPushRequest, db: AsyncSession = Depends(get_db)):
    """
    執行批次個案推播
    - 自動依據工號綁定寫入通知記錄表 (NotificationLog) 並儲存資安脫敏內文
    - 若業務員已完成 LINE 身分綁定，自動傳送 LINE Flex Card 推播訊息給業務員手機
    """
    notification = Notification(
        title=payload.push_title,
        category="行政照會",
        content_summary=f"批次推播共 {len(payload.items)} 筆",
        push_type="individual_excel",
        created_by="admin"
    )
    db.add(notification)
    await db.flush()

    sent_count = 0
    failed_count = 0
    now = datetime.now(timezone.utc)

    for item in payload.items:
        result = await db.execute(select(Agent).where(Agent.agent_code == item.agent_code))
        agent = result.scalar_one_or_none()

        if not agent:
            failed_count += 1
            continue

        target_line_user_id = agent.line_user_id or f"U_MOCK_{agent.agent_code}"

        flex_json = LineFlexBuilder.build_notification_card(
            category=item.category,
            title=item.title,
            masked_content=item.masked_content or item.raw_content
        )

        if agent.line_user_id:
            await LineMessagingService.push_message(agent.line_user_id, flex_json)

        log = NotificationLog(
            notification_id=notification.id,
            agent_id=agent.id,
            line_user_id=target_line_user_id,
            category=item.category,
            title=item.title,
            masked_content=item.masked_content or item.raw_content,
            raw_content=item.raw_content or item.masked_content,
            flex_message_json=flex_json,
            send_type="push",
            status="sent",
            sent_at=now
        )
        db.add(log)
        sent_count += 1

    await db.commit()
    return {
        "notification_id": str(notification.id),
        "total_items": len(payload.items),
        "sent_count": sent_count,
        "failed_count": failed_count,
        "message": f"批次推播已處理完畢，成功發送 {sent_count} 筆，失敗 {failed_count} 筆"
    }


class BroadcastPushRequest(BaseModel):
    target_type: str  # 'all', 'job_title', 'branch', 'district', 'channel'
    target_values: Optional[List[str]] = []  # 多選標籤陣列
    target_value: Optional[str] = None  # 單選相容性
    category: str  # '行政照會', '商品異動', '營運活動'
    title: str
    raw_content: str


@router.post("/execute-broadcast-push")
async def execute_broadcast_push(payload: BroadcastPushRequest, db: AsyncSession = Depends(get_db)):
    """
    發送全體 / 分眾標籤廣播通知 (支援通路 >> 督導區 >> 通訊處 >> 職級 多選標籤)
    """
    stmt = select(Agent).where(Agent.status == "active")

    selected_values = list(payload.target_values or [])
    if payload.target_value and payload.target_value not in selected_values:
        selected_values.append(payload.target_value)

    if payload.target_type == "job_title" and selected_values and "all" not in selected_values:
        job_prefixes = [v.split(" ")[0] for v in selected_values if v]
        or_clauses = [Agent.job_title.like(f"%{pref}%") for pref in job_prefixes]
        if or_clauses:
            stmt = stmt.where(or_(*or_clauses))
    elif payload.target_type == "district" and selected_values and "all" not in selected_values:
        stmt = stmt.where(Agent.district.in_(selected_values))
    elif payload.target_type == "branch" and selected_values and "all" not in selected_values:
        stmt = stmt.where(Agent.branch_office.in_(selected_values))
    elif payload.target_type == "channel" and selected_values and "all" not in selected_values:
        stmt = stmt.where(Agent.channel.in_(selected_values))

    result = await db.execute(stmt)
    target_agents = result.scalars().all()

    if not target_agents:
        raise HTTPException(status_code=400, detail="符合該分眾複選條件的在職業務員人數為 0 人，無法發送")

    masked_content = DataMaskingService.sanitize_text(payload.raw_content)

    targets_str = ", ".join(selected_values) if selected_values else "全體"

    notification = Notification(
        title=payload.title,
        category=payload.category,
        content_summary=f"分眾廣播 ({payload.target_type}: {targets_str}) 共 {len(target_agents)} 人",
        push_type="broadcast_tag",
        created_by="admin"
    )
    db.add(notification)
    await db.flush()

    sent_count = 0
    failed_count = 0
    now = datetime.now(timezone.utc)

    for agent in target_agents:
        target_line_user_id = agent.line_user_id or f"U_MOCK_{agent.agent_code}"
        flex_json = LineFlexBuilder.build_notification_card(
            category=payload.category,
            title=payload.title,
            masked_content=masked_content
        )

        if agent.line_user_id:
            await LineMessagingService.push_message(agent.line_user_id, flex_json)

        log = NotificationLog(
            notification_id=notification.id,
            agent_id=agent.id,
            line_user_id=target_line_user_id,
            category=payload.category,
            title=payload.title,
            masked_content=masked_content,
            raw_content=payload.raw_content,
            flex_message_json=flex_json,
            send_type="push",
            status="sent",
            sent_at=now
        )
        db.add(log)
        sent_count += 1

    await db.commit()
    return {
        "notification_id": str(notification.id),
        "target_count": len(target_agents),
        "sent_count": sent_count,
        "failed_count": failed_count,
        "message": f"分眾廣播已成功推播給 {sent_count} 位符合條件的業務員！ (涵蓋標籤: {targets_str})"
    }


@router.get("/agents")
async def list_agents(db: AsyncSession = Depends(get_db)):
    """查詢所有業務員綁定與最新主檔狀態"""
    result = await db.execute(select(Agent))
    agents = result.scalars().all()
    return [
        {
            "id": str(a.id),
            "agent_code": a.agent_code,
            "name": a.name,
            "phone": a.phone,
            "channel": a.channel or "-",
            "district": a.district or "-",
            "branch_office": a.branch_office or "-",
            "job_title": a.job_title or "-",
            "status": a.status,
            "line_user_id": a.line_user_id,
            "is_verified": a.is_verified,
            "is_bound_real_line": bool(a.line_user_id and not a.line_user_id.startswith("U_MOCK"))
        }
        for a in agents
    ]


class ManualBindRequest(BaseModel):
    agent_code: str
    line_user_id: str


@router.post("/bind-line-id")
async def manual_bind_line_id(payload: ManualBindRequest, db: AsyncSession = Depends(get_db)):
    """手動綁定業務員 LINE User ID (測試用)"""
    result = await db.execute(select(Agent).where(Agent.agent_code == payload.agent_code))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="查無此業務員")
    agent.line_user_id = payload.line_user_id
    agent.is_verified = True
    await db.commit()
    return {"status": "success", "agent_code": agent.agent_code, "line_user_id": agent.line_user_id}
