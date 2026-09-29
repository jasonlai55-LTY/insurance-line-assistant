from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class OTPRequest(BaseModel):
    agent_code: str = Field(..., description="業務員工號")
    phone: str = Field(..., description="業務員手機號碼")


class OTPVerifyRequest(BaseModel):
    agent_code: str = Field(..., description="業務員工號")
    phone: str = Field(..., description="業務員手機號碼")
    otp_code: str = Field(..., min_length=6, max_length=6, description="6 位數 OTP 驗證碼")
    line_user_id: Optional[str] = Field(None, description="LINE User ID (自 LIFF 帶入)")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    agent_code: str
    name: str
    is_verified: bool


class AgentResponse(BaseModel):
    id: uuid.UUID
    agent_code: str
    name: str
    phone: str
    channel: str
    branch_office: str
    job_title: str
    line_user_id: Optional[str] = None
    is_verified: bool
    status: str

    class Config:
        from_attributes = True


class AdminLoginRequest(BaseModel):
    username: str
    password: str
