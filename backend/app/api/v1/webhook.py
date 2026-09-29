from fastapi import APIRouter, Request, Header, HTTPException, Depends, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.config import settings
from app.db.models import Agent, ProductAsset, Category
from app.services.line_service import LineFlexBuilder, LineMessagingService
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

router = APIRouter()


class WebhookPayload(BaseModel):
    events: List[Dict[str, Any]] = []


@router.post("/webhook")
async def line_webhook(
    payload: WebhookPayload = Body(...),
    x_line_signature: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    LINE Webhook 接收點
    - 處理 follow 事件（新好友加入迎賓卡片 & 自動綁定 LINE User ID）
    - 處理 message 文字搜尋（搜尋商品代號與行政規範 & 自動綁定 LINE User ID）
    """
    try:
        events = payload.events
        processed_count = 0

        for event in events:
            print(f"[LINE Webhook Event Received] {event}")
            event_type = event.get("type")
            reply_token = event.get("replyToken")
            user_id = event.get("source", {}).get("userId")

            # 若有真正的 LINE User ID，且業務員尚未綁定，自動更新 Agent A001 之 line_user_id
            if user_id:
                result = await db.execute(select(Agent).where(Agent.agent_code == "A001"))
                agent = result.scalar_one_or_none()
                if agent and (not agent.line_user_id or agent.line_user_id.startswith("U_MOCK")):
                    agent.line_user_id = user_id
                    await db.commit()
                    print(f"✅ [LINE Webhook] 成功將 Agent A001 綁定至真實 LINE User ID: {user_id}")

            # 1. 處理加入好友 (follow)
            if event_type == "follow":
                welcome_card = LineFlexBuilder.build_welcome_card()
                if reply_token:
                    await LineMessagingService.reply_message(reply_token, welcome_card)
                processed_count += 1

            # 2. 處理文字訊息 (message)
            elif event_type == "message" and event.get("message", {}).get("type") == "text":
                text = event["message"]["text"].strip()
                menu_keywords = ["選單", "主選單", "首頁", "開通", "目錄", "功能", "幫助", "hi", "hello", "menu", "help", "1"]

                if any(kw in text.lower() for kw in menu_keywords):
                    menu_card = LineFlexBuilder.build_welcome_card()
                    if reply_token:
                        await LineMessagingService.reply_message(reply_token, menu_card)
                else:
                    # 關鍵字或商品代號搜尋
                    query = select(ProductAsset).where(
                        ProductAsset.status == "published",
                        (ProductAsset.product_code.ilike(f"%{text}%")) | (ProductAsset.title.ilike(f"%{text}%"))
                    ).limit(3)
                    result = await db.execute(query)
                    assets = result.scalars().all()

                    if assets:
                        flex_cards = []
                        for asset in assets:
                            card = LineFlexBuilder.build_product_card(
                                product_code=asset.product_code or "N/A",
                                title=asset.title,
                                category_name=asset.type,
                                file_url=asset.file_url,
                                description=asset.description
                            )
                            flex_cards.append(card)
                        
                        if reply_token:
                            await LineMessagingService.reply_message(reply_token, flex_cards[0])
                    else:
                        menu_card = LineFlexBuilder.build_welcome_card()
                        if reply_token:
                            await LineMessagingService.reply_message(reply_token, menu_card)

                processed_count += 1

        return {"status": "success", "processed_events": processed_count}
    except Exception as e:
        print("Webhook error:", e)
        return {"status": "error", "message": str(e)}
