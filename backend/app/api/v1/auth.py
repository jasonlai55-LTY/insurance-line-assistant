from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import create_access_token, verify_password, get_password_hash
from app.db.models import Agent, AdminUser
from app.schemas.auth import OTPRequest, OTPVerifyRequest, TokenResponse, AgentResponse, AdminLoginRequest
from app.services.otp_service import OTPService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/request-otp")
async def request_otp(payload: OTPRequest, db: AsyncSession = Depends(get_db)):
    """發送簡訊 OTP 驗證碼"""
    otp_code = await OTPService.request_otp(db, agent_code=payload.agent_code, phone=payload.phone)
    return {"message": "驗證碼已傳送至您的手機", "mock_otp": otp_code}


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(payload: OTPVerifyRequest, db: AsyncSession = Depends(get_db)):
    """驗證簡訊 OTP，完成工號綁定並發放 JWT Token"""
    agent = await OTPService.verify_otp(
        db,
        agent_code=payload.agent_code,
        phone=payload.phone,
        otp_code=payload.otp_code,
        line_user_id=payload.line_user_id
    )
    
    token = create_access_token(subject=agent.agent_code)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        agent_code=agent.agent_code,
        name=agent.name,
        is_verified=agent.is_verified
    )


from pydantic import BaseModel

class LineIdLoginRequest(BaseModel):
    line_user_id: str


@router.post("/auto-login-by-line-id", response_model=TokenResponse)
async def auto_login_by_line_id(payload: LineIdLoginRequest, db: AsyncSession = Depends(get_db)):
    """若該 LINE User ID 已完成綁定，直接發放 JWT Token 完成免登入體驗"""
    result = await db.execute(select(Agent).where(Agent.line_user_id == payload.line_user_id, Agent.is_verified == True, Agent.status == "active"))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="尚未完成工號與 LINE 帳號綁定或帳號已離職停用")
    
    token = create_access_token(subject=agent.agent_code)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        agent_code=agent.agent_code,
        name=agent.name,
        is_verified=agent.is_verified
    )



@router.post("/admin/login")
async def admin_login(payload: AdminLoginRequest, db: AsyncSession = Depends(get_db)):
    """後台管理者登入"""
    result = await db.execute(select(AdminUser).where(AdminUser.username == payload.username))
    admin = result.scalar_one_or_none()
    
    # 預設開發環境管理者密碼防呆自動建立
    if not admin and payload.username == "admin" and payload.password == "admin123":
        admin = AdminUser(username="admin", hashed_password=get_password_hash("admin123"), role="admin")
        db.add(admin)
        await db.commit()
        await db.refresh(admin)

    if not admin or not verify_password(payload.password, admin.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="帳號或密碼錯誤")

    token = create_access_token(subject=f"admin:{admin.username}")
    return {"access_token": token, "token_type": "bearer", "username": admin.username}
