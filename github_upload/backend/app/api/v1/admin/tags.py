import uuid
from io import BytesIO
from typing import List, Optional
import openpyxl
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.db.models import Tag
from pydantic import BaseModel

router = APIRouter(prefix="/admin/tags", tags=["CMS Tag Management"])


class TagCreate(BaseModel):
    tag_name: str
    tag_category: str  # 'channel', 'branch', 'job_title', 'custom'


class TagUpdate(BaseModel):
    tag_name: str
    tag_category: str


@router.get("")
async def list_tags(db: AsyncSession = Depends(get_db)):
    """取得全部分眾標籤 (通路、通訊處、職級)"""
    result = await db.execute(select(Tag).order_by(Tag.tag_category, Tag.tag_name))
    tags = result.scalars().all()
    return [{"id": str(t.id), "tag_name": t.tag_name, "tag_category": t.tag_category} for t in tags]


@router.post("")
async def create_tag(payload: TagCreate, db: AsyncSession = Depends(get_db)):
    """新增分眾標籤"""
    tag = Tag(tag_name=payload.tag_name, tag_category=payload.tag_category)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return {"id": str(tag.id), "tag_name": tag.tag_name, "tag_category": tag.tag_category}


@router.post("/batch-import-excel")
async def batch_import_tags_excel(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """
    Excel 批次匯入分眾標籤
    - 標頭需求：標籤名稱, 標籤分類
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

    name_col_idx = None
    for c in ["標籤名稱", "tag_name", "名稱"]:
        if c in header_map:
            name_col_idx = header_map[c]
            break

    cat_col_idx = None
    for c in ["標籤分類", "tag_category", "分類"]:
        if c in header_map:
            cat_col_idx = header_map[c]
            break

    if name_col_idx is None or cat_col_idx is None:
        raise HTTPException(status_code=400, detail="Excel 缺少必要標頭：必須包含 '標籤名稱' 與 '標籤分類'")

    imported_count = 0
    skipped_count = 0

    existing_result = await db.execute(select(Tag))
    existing_names = set(t.tag_name for t in existing_result.scalars().all())

    cat_map = {
        "職級": "job_title",
        "job_title": "job_title",
        "督導區": "district",
        "區部": "district",
        "district": "district",
        "通訊處": "branch",
        "單位": "branch",
        "branch": "branch",
        "通路": "channel",
        "channel": "channel"
    }

    def get_val(row_data, idx):
        if idx is None or idx >= len(row_data):
            return None
        val = row_data[idx]
        if val is None:
            return None
        s = str(val).strip()
        return s if s != "" else None

    for row in rows[1:]:
        raw_name = get_val(row, name_col_idx) or ""
        raw_cat = get_val(row, cat_col_idx) or ""

        if not raw_name:
            continue

        if raw_name in existing_names:
            skipped_count += 1
            continue

        mapped_cat = cat_map.get(raw_cat, "custom") if raw_cat else "custom"
        tag = Tag(tag_name=raw_name, tag_category=mapped_cat)
        db.add(tag)
        existing_names.add(raw_name)
        imported_count += 1

    await db.commit()
    return {
        "imported_count": imported_count,
        "skipped_count": skipped_count,
        "message": f"成功匯入 {imported_count} 個新標籤 (跳過 {skipped_count} 個重複標籤)"
    }


@router.put("/{tag_id}")
async def update_tag(tag_id: uuid.UUID, payload: TagUpdate, db: AsyncSession = Depends(get_db)):
    """更新分眾標籤"""
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    tag.tag_name = payload.tag_name
    tag.tag_category = payload.tag_category
    await db.commit()
    await db.refresh(tag)
    return {"id": str(tag.id), "tag_name": tag.tag_name, "tag_category": tag.tag_category}


@router.delete("/{tag_id}")
async def delete_tag(tag_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """刪除分眾標籤"""
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    await db.delete(tag)
    await db.commit()
    return {"status": "success", "message": f"Tag {tag_id} deleted"}
