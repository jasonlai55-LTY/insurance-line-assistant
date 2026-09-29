from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import verify_token
from app.db.models import Agent, ProductAsset, Category
from app.schemas.product import ProductAssetResponse, CategoryResponse
from app.services.asset_service import AssetService

router = APIRouter(prefix="/products", tags=["Products & Guidelines"])


async def get_current_agent_verified_status(authorization: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)) -> bool:
    """從 JWT Header 檢查業務員是否通過 OTP 驗證"""
    if not authorization or not authorization.startswith("Bearer "):
        return False
    token = authorization.split(" ")[1]
    agent_code = verify_token(token)
    if not agent_code or agent_code.startswith("admin:"):
        return False

    result = await db.execute(select(Agent).where(Agent.agent_code == agent_code, Agent.status == "active"))
    agent = result.scalar_one_or_none()
    return agent.is_verified if agent else False


@router.get("/categories", response_model=List[CategoryResponse])
async def list_categories(type: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """取得素材與規範分類標籤列表"""
    stmt = select(Category)
    if type:
        stmt = stmt.where(Category.type == type)
    stmt = stmt.order_by(Category.sort_order.asc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/assets", response_model=List[ProductAssetResponse])
async def list_assets(
    type: Optional[str] = Query(None, description="'product' 或 'admin_rule'"),
    product_code: Optional[str] = Query(None, description="商品代號如 ACC01"),
    category_id: Optional[str] = Query(None),
    is_verified: bool = Depends(get_current_agent_verified_status),
    db: AsyncSession = Depends(get_db)
):
    """
    查詢商品 DM、銷售手冊、行政規範與理賠表單
    - 資安規範：若未通過 OTP 驗證，內部限閱文件 (is_internal_only == True) 會自動被隱藏/阻擋
    """
    assets = await AssetService.get_published_assets(
        db,
        asset_type=type,
        product_code=product_code,
        category_id=category_id,
        is_verified=is_verified
    )

    response_list = []
    for a in assets:
        is_expired = AssetService.check_is_expired(a.expiration_date)
        resp = ProductAssetResponse(
            id=a.id,
            type=a.type,
            product_code=a.product_code,
            title=a.title,
            category_id=a.category_id,
            category_name=a.category.name if a.category else None,
            file_url=a.file_url,
            thumbnail_url=a.thumbnail_url,
            description=a.description,
            is_internal_only=a.is_internal_only,
            status=a.status,
            effective_date=a.effective_date,
            expiration_date=a.expiration_date,
            is_expired=is_expired,
            created_at=a.created_at
        )
        response_list.append(resp)

    return response_list
