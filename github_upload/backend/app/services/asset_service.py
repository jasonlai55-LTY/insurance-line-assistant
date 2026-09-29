from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import ProductAsset, Category
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status


class AssetService:
    @staticmethod
    async def get_published_assets(
        db: AsyncSession,
        asset_type: Optional[str] = None,
        product_code: Optional[str] = None,
        category_id: Optional[str] = None,
        is_verified: bool = False
    ) -> List[ProductAsset]:
        """
        取得已發佈素材/規範：
        - 若業務員未通過 OTP 驗證 (is_verified == False)，自動過濾 is_internal_only == True 之限內部文件。
        """
        stmt = select(ProductAsset).options(selectinload(ProductAsset.category)).where(ProductAsset.status == "published")

        if asset_type:
            stmt = stmt.where(ProductAsset.type == asset_type)
        if product_code:
            stmt = stmt.where(ProductAsset.product_code == product_code)
        if category_id:
            stmt = stmt.where(ProductAsset.category_id == category_id)

        # 資安防護：未驗證業務員不可存取限內部文件
        if not is_verified:
            stmt = stmt.where(ProductAsset.is_internal_only == False)

        stmt = stmt.order_by(ProductAsset.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    def check_is_expired(expiration_date: Optional[datetime]) -> bool:
        """過期日警示計算 (安全相容 offset-naive 與 offset-aware datetime)"""
        if not expiration_date:
            return False
        try:
            now = datetime.now(timezone.utc)
            if expiration_date.tzinfo is None:
                expiration_date = expiration_date.replace(tzinfo=timezone.utc)
            return expiration_date < now
        except Exception:
            return False

