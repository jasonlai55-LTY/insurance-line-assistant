import uuid
from io import BytesIO
from typing import List, Optional
import openpyxl
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.db.models import ProductAsset, Category
from app.schemas.product import ProductAssetCreate, ProductAssetResponse, CategoryResponse
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["CMS Asset & Category Management"])


class CategoryCreate(BaseModel):
    type: str  # 'product_asset', 'administrative_rule', 'notification_category'
    name: str
    sort_order: int = 0


@router.get("/categories", response_model=List[CategoryResponse])
async def admin_list_categories(type: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """查詢分類清單 (支援商品、行政規範、通知分類)"""
    stmt = select(Category)
    if type:
        stmt = stmt.where(Category.type == type)
    stmt = stmt.order_by(Category.sort_order.asc(), Category.created_at.asc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/categories", response_model=CategoryResponse)
async def admin_create_category(payload: CategoryCreate, db: AsyncSession = Depends(get_db)):
    """新增分類 (可自訂通知分類、素材分類名稱)"""
    cat = Category(type=payload.type, name=payload.name, sort_order=payload.sort_order)
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return cat


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def admin_update_category(category_id: str, payload: CategoryCreate, db: AsyncSession = Depends(get_db)):
    """編輯/重命名分類名稱與排序"""
    target_id = category_id
    try:
        target_id = uuid.UUID(category_id)
    except Exception:
        pass

    result = await db.execute(select(Category).where(Category.id == target_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail=f"找不到該分類: {category_id}")

    cat.name = payload.name
    cat.type = payload.type
    cat.sort_order = payload.sort_order
    await db.commit()
    await db.refresh(cat)
    return cat


@router.delete("/categories/{category_id}")
async def admin_delete_category(category_id: str, db: AsyncSession = Depends(get_db)):
    """刪除分類"""
    target_id = category_id
    try:
        target_id = uuid.UUID(category_id)
    except Exception:
        pass

    await db.execute(delete(Category).where(Category.id == target_id))
    await db.commit()
    return {"message": "分類已成功刪除"}


# --- Asset CRUD ---

@router.get("/assets", response_model=List[ProductAssetResponse])
async def admin_list_assets(type: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """後台管理者查詢所有素材 (包含急載入 Category 關係)"""
    stmt = select(ProductAsset).options(selectinload(ProductAsset.category))
    if type:
        stmt = stmt.where(ProductAsset.type == type)
    stmt = stmt.order_by(ProductAsset.created_at.desc())
    result = await db.execute(stmt)
    assets = result.scalars().all()

    response_list = []
    for a in assets:
        resp = ProductAssetResponse(
            id=a.id,
            type=a.type,
            product_code=a.product_code,
            title=a.title,
            category_id=a.category_id,
            category_name=a.category.name if a.category else "通用規範",
            file_url=a.file_url,
            thumbnail_url=a.thumbnail_url,
            description=a.description,
            is_internal_only=a.is_internal_only,
            status=a.status,
            effective_date=a.effective_date,
            expiration_date=a.expiration_date,
            is_expired=False,
            created_at=a.created_at
        )
        response_list.append(resp)
    return response_list


@router.post("/assets", response_model=ProductAssetResponse)
async def admin_create_asset(payload: ProductAssetCreate, db: AsyncSession = Depends(get_db)):
    """新增商品素材或行政規範"""
    cat_id = None
    if payload.category_id:
        try:
            cat_id = uuid.UUID(str(payload.category_id))
        except Exception:
            pass

    cat = None
    if payload.category_name and payload.category_name.strip():
        c_name = payload.category_name.strip()
        cat_search = await db.execute(select(Category).where(Category.type == payload.type, Category.name == c_name))
        cat = cat_search.scalar_one_or_none()
        if not cat:
            cat = Category(type=payload.type, name=c_name, sort_order=10)
            db.add(cat)
            await db.flush()
        cat_id = cat.id

    if not cat and cat_id:
        cat_check = await db.execute(select(Category).where(Category.id == cat_id))
        cat = cat_check.scalar_one_or_none()

    if not cat:
        cat_first = await db.execute(select(Category).where(Category.type == payload.type).limit(1))
        cat = cat_first.scalar_one_or_none()
        if not cat:
            cat = Category(type=payload.type, name="通用規範", sort_order=1)
            db.add(cat)
            await db.flush()
        cat_id = cat.id

    asset = ProductAsset(
        type=payload.type,
        product_code=payload.product_code.strip() if (payload.product_code and payload.product_code.strip()) else None,
        title=payload.title,
        category_id=cat_id,
        file_url=payload.file_url,
        thumbnail_url=payload.thumbnail_url,
        description=payload.description,
        is_internal_only=payload.is_internal_only,
        status="published",
        effective_date=payload.effective_date,
        expiration_date=payload.expiration_date,
        created_by="admin"
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)

    cat_res = await db.execute(select(Category).where(Category.id == cat_id))
    cat_obj = cat_res.scalar_one_or_none()

    return ProductAssetResponse(
        id=asset.id,
        type=asset.type,
        product_code=asset.product_code,
        title=asset.title,
        category_id=asset.category_id,
        category_name=cat_obj.name if cat_obj else "通用規範",
        file_url=asset.file_url,
        thumbnail_url=asset.thumbnail_url,
        description=asset.description,
        is_internal_only=asset.is_internal_only,
        status=asset.status,
        effective_date=asset.effective_date,
        expiration_date=asset.expiration_date,
        is_expired=False,
        created_at=asset.created_at
    )


@router.post("/assets/batch-import-excel")
async def batch_import_assets_excel(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """
    Excel 批次匯入商品素材與行政規範表單
    - 標頭欄位需求：素材標題 (必須), 類別 (商品素材/行政規範表單), 商品代號 (選填), 檔案網址 (選填), 內部權限 (選填)
    """
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="僅支援 .xlsx 或 .xls 格式之 Excel 檔案")

    content = await file.read()
    try:
        wb = openpyxl.load_workbook(BytesIO(content), data_only=True)
        ws = wb.active
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Excel 檔案無法解析: {str(e)}")

    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        raise HTTPException(status_code=400, detail="Excel 檔案無數據")

    headers = [str(cell).strip() if cell is not None else "" for cell in rows[0]]
    header_map = {name: idx for idx, name in enumerate(headers)}

    title_col_idx = None
    for c in ["素材標題", "標題", "title"]:
        if c in header_map:
            title_col_idx = header_map[c]
            break

    if title_col_idx is None:
        raise HTTPException(status_code=400, detail="Excel 缺少必要標頭：必須包含 '素材標題'")

    type_col_idx = None
    for c in ["類別", "素材類型", "type"]:
        if c in header_map:
            type_col_idx = header_map[c]
            break

    code_col_idx = None
    for c in ["商品代號", "product_code"]:
        if c in header_map:
            code_col_idx = header_map[c]
            break

    url_col_idx = None
    for c in ["檔案網址", "file_url", "網址"]:
        if c in header_map:
            url_col_idx = header_map[c]
            break

    perm_col_idx = None
    for c in ["內部權限", "is_internal_only", "限業務存取"]:
        if c in header_map:
            perm_col_idx = header_map[c]
            break

    def get_val(row_data, idx):
        if idx is None or idx >= len(row_data):
            return None
        val = row_data[idx]
        if val is None:
            return None
        s = str(val).strip()
        return s if s != "" else None

    imported_count = 0

    cat_res = await db.execute(select(Category).limit(1))
    cat_default = cat_res.scalar_one_or_none()
    if not cat_default:
        cat_default = Category(type="admin_rule", name="通用規範", sort_order=1)
        db.add(cat_default)
        await db.flush()

    for row in rows[1:]:
        raw_title = get_val(row, title_col_idx) or ""
        if not raw_title:
            continue

        raw_type_val = get_val(row, type_col_idx) or "admin_rule"
        asset_type = "product" if ("商品" in raw_type_val or raw_type_val == "product") else "admin_rule"

        raw_code = get_val(row, code_col_idx)
        if raw_code == "" or raw_code == "nan":
            raw_code = None

        raw_url = get_val(row, url_col_idx) or "https://example.com/file.pdf"

        raw_perm = get_val(row, perm_col_idx) or "否"
        is_internal = True if (raw_perm in ["是", "true", "True", "1"]) else False

        asset = ProductAsset(
            type=asset_type,
            product_code=raw_code,
            title=raw_title,
            category_id=cat_default.id,
            file_url=raw_url,
            status="published",
            is_internal_only=is_internal,
            created_by="admin"
        )
        db.add(asset)
        imported_count += 1

    await db.commit()
    return {
        "imported_count": imported_count,
        "message": f"成功匯入 {imported_count} 筆素材與規範表單！"
    }


@router.put("/assets/{asset_id}/status")
async def admin_update_asset_status(asset_id: str, status_val: str, db: AsyncSession = Depends(get_db)):
    """更新素材上架/下架狀態"""
    if status_val not in ["published", "draft", "archived"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="無效的狀態值")

    target_id = asset_id
    try:
        target_id = uuid.UUID(asset_id)
    except Exception:
        pass

    await db.execute(
        update(ProductAsset).where(ProductAsset.id == target_id).values(status=status_val)
    )
    await db.commit()
    return {"message": f"素材狀態已更新為 {status_val}"}


@router.delete("/assets/{asset_id}")
async def admin_delete_asset(asset_id: str, db: AsyncSession = Depends(get_db)):
    """刪除素材與行政規範"""
    target_id = asset_id
    try:
        target_id = uuid.UUID(asset_id)
    except Exception:
        pass

    result = await db.execute(select(ProductAsset).where(ProductAsset.id == target_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="找不到該素材或規範")

    await db.delete(asset)
    await db.commit()
    return {"message": f"素材 '{asset.title}' 已成功刪除"}


@router.put("/assets/{asset_id}", response_model=ProductAssetResponse)
async def admin_update_asset(asset_id: str, payload: ProductAssetCreate, db: AsyncSession = Depends(get_db)):
    """編輯商品素材或行政規範資訊"""
    target_id = asset_id
    try:
        target_id = uuid.UUID(asset_id)
    except Exception:
        pass

    result = await db.execute(select(ProductAsset).where(ProductAsset.id == target_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="找不到該素材或規範")

    asset.title = payload.title
    asset.type = payload.type
    asset.product_code = payload.product_code.strip() if (payload.product_code and payload.product_code.strip()) else None
    asset.file_url = payload.file_url
    asset.is_internal_only = payload.is_internal_only
    if payload.description:
        asset.description = payload.description

    if payload.category_name and payload.category_name.strip():
        c_name = payload.category_name.strip()
        cat_search = await db.execute(select(Category).where(Category.type == payload.type, Category.name == c_name))
        cat_find = cat_search.scalar_one_or_none()
        if not cat_find:
            cat_find = Category(type=payload.type, name=c_name, sort_order=10)
            db.add(cat_find)
            await db.flush()
        asset.category_id = cat_find.id

    await db.commit()
    await db.refresh(asset)

    cat_res = await db.execute(select(Category).where(Category.id == asset.category_id))
    cat_obj = cat_res.scalar_one_or_none()

    return ProductAssetResponse(
        id=asset.id,
        type=asset.type,
        product_code=asset.product_code,
        title=asset.title,
        category_id=asset.category_id,
        category_name=cat_obj.name if cat_obj else "通用規範",
        file_url=asset.file_url,
        thumbnail_url=asset.thumbnail_url,
        description=asset.description,
        is_internal_only=asset.is_internal_only,
        status=asset.status,
        effective_date=asset.effective_date,
        expiration_date=asset.expiration_date,
        is_expired=False,
        created_at=asset.created_at
    )

