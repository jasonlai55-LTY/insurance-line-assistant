from pydantic import BaseModel, Field
from typing import Optional, List, Union, Any
from datetime import datetime
import uuid


class CategoryResponse(BaseModel):
    id: uuid.UUID
    type: str
    name: str
    sort_order: int

    class Config:
        from_attributes = True


class ProductAssetCreate(BaseModel):
    type: str = Field("product", description="'product' 或 'admin_rule'")
    product_code: Optional[str] = Field(None, description="商品代號如 ACC01")
    title: str = Field(..., description="素材/規範名稱")
    category_id: Optional[Any] = Field(None, description="分類 ID (選填，空值將自動歸類)")
    category_name: Optional[str] = Field(None, description="分類名稱如：投保規則、保費規則")
    file_url: str
    thumbnail_url: Optional[str] = None
    description: Optional[str] = None
    is_internal_only: bool = True
    effective_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None



class ProductAssetResponse(BaseModel):
    id: uuid.UUID
    type: str
    product_code: Optional[str] = None
    title: str
    category_id: uuid.UUID
    category_name: Optional[str] = None
    file_url: str
    thumbnail_url: Optional[str] = None
    description: Optional[str] = None
    is_internal_only: bool
    status: str
    effective_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    is_expired: bool = False
    created_at: datetime

    class Config:
        from_attributes = True
