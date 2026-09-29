from pydantic import BaseModel
from typing import Optional, List, Any, Dict


class LineWebhookEvent(BaseModel):
    type: str
    replyToken: Optional[str] = None
    source: Dict[str, Any]
    message: Optional[Dict[str, Any]] = None
    timestamp: int
