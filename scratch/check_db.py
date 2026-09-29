import sys, os
os.environ["USE_SQLITE"] = "1"
sys.path.insert(0, os.path.abspath("backend"))
import asyncio
from app.core.database import AsyncSessionLocal
from app.db.models import Agent, OTPRecord
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Agent))
        agents = res.scalars().all()
        print("=== AGENTS ===")
        for a in agents:
            print(f"Code: {a.agent_code}, Name: {a.name}, Phone: {a.phone}, LineID: {a.line_user_id}, Verified: {a.is_verified}")

        res2 = await db.execute(select(OTPRecord))
        otps = res2.scalars().all()
        print("\n=== OTP RECORDS ===")
        for o in otps:
            print(f"Code: {o.agent_code}, Phone: {o.phone}, OTP: {o.otp_code}, Used: {o.is_used}, Exp: {o.expires_at}")

if __name__ == "__main__":
    asyncio.run(check())
