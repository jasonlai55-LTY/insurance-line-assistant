from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime
import uuid


class NotificationLogResponse(BaseModel):
    id: uuid.UUID
    category: str
    title: str
    masked_content: str
    raw_content: Optional[str] = None
    flex_message_json: Optional[Dict[str, Any]] = None
    send_type: str
    status: str
    sent_at: Optional[datetime] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class BatchPushItem(BaseModel):
    agent_code: str = Field(..., description="業務員工號")
    category: str = Field(..., description="通知類別: 行政照會 | 商品異動 | 營運活動")
    title: str = Field(..., description="通知標題")
    raw_content: Optional[str] = Field(None, description="未脫敏原始內文")
    masked_content: Optional[str] = Field(None, description="脫敏內文")


class BatchPushRequest(BaseModel):
    push_title: str = Field(..., description="批次任務標題")
    items: List[BatchPushItem]


class TagPushRequest(BaseModel):
    title: str
    category: str
    content: str
    target_tags: List[str] = Field(..., description="選取的標籤列表")
