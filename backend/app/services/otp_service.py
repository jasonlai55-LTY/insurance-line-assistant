import random
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Agent, OTPRecord
from fastapi import HTTPException, status


class OTPService:
    @staticmethod
    def generate_otp_code() -> str:
        """產生 6 位數字 OTP"""
        return f"{random.randint(100000, 999999)}"

    @classmethod
    async def request_otp(cls, db: AsyncSession, agent_code: str, phone: str) -> str:
        """
        請求發送 OTP:
        1. 檢查業務員工號與手機是否匹配
        2. 產出 OTP 並存入 otp_records 表
        """
        result = await db.execute(
            select(Agent).where(Agent.agent_code == agent_code, Agent.phone == phone)
        )
        agent = result.scalar_one_or_none()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="工號或手機號碼不正確，無法傳送驗證碼"
            )

        otp_code = cls.generate_otp_code()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

        otp_record = OTPRecord(
            agent_code=agent_code,
            phone=phone,
            otp_code=otp_code,
            expires_at=expires_at,
            is_used=False
        )
        db.add(otp_record)
        await db.commit()

        # 在實際環境中在此處整合 SMS API (如三竹簡訊)
        print(f"[SMS OTP Simulator] Agent {agent_code} ({phone}) OTP: {otp_code}")
        return otp_code

    @classmethod
    async def verify_otp(
        cls, db: AsyncSession, agent_code: str, phone: str, otp_code: str, line_user_id: str = None
    ) -> Agent:
        """
        驗證 OTP 並綁定 LINE User ID
        """
        now = datetime.now(timezone.utc)
        result = await db.execute(
            select(OTPRecord)
            .where(
                OTPRecord.agent_code == agent_code,
                OTPRecord.phone == phone,
                OTPRecord.otp_code == otp_code,
                OTPRecord.is_used == False,
                OTPRecord.expires_at >= now
            )
            .order_by(OTPRecord.created_at.desc())
        )
        record = result.scalars().first()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="驗證碼錯誤或已逾期"
            )

        # 標記 OTP 已使用
        record.is_used = True

        # 更新 Agent 狀態為已驗證
        agent_result = await db.execute(
            select(Agent).where(Agent.agent_code == agent_code)
        )
        agent = agent_result.scalar_one_or_none()
        if agent:
            agent.is_verified = True
            agent.verified_at = now
            if line_user_id:
                agent.line_user_id = line_user_id
            await db.commit()
            await db.refresh(agent)

        return agent
