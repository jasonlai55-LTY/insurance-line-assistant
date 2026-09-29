import uuid
from io import BytesIO
from typing import List, Optional
import openpyxl
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.core.database import get_db
from app.db.models import Agent
from pydantic import BaseModel

router = APIRouter(prefix="/admin/agents", tags=["CMS Agent Master Data Management"])


class AgentCreate(BaseModel):
    agent_code: str
    name: str
    phone: str
    channel: Optional[str] = "直營"
    district: Optional[str] = "台北督導區"
    branch_office: Optional[str] = "台北一處"
    job_title: Optional[str] = "區經理"


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    channel: Optional[str] = None
    district: Optional[str] = None
    branch_office: Optional[str] = None
    job_title: Optional[str] = None
    status: Optional[str] = None  # 'active', 'resigned', 'suspended'


@router.get("")
async def list_agents(
    query: Optional[str] = Query(None, description="搜尋姓名、工號、督導區、通訊處或職級"),
    status: Optional[str] = Query(None, description="過濾狀態 (active, resigned, suspended)"),
    db: AsyncSession = Depends(get_db)
):
    """查詢所有業務員主資料"""
    stmt = select(Agent).order_by(Agent.agent_code)

    if status:
        stmt = stmt.where(Agent.status == status)

    if query:
        q = f"%{query.strip()}%"
        stmt = stmt.where(
            or_(
                Agent.agent_code.ilike(q),
                Agent.name.ilike(q),
                Agent.district.ilike(q),
                Agent.branch_office.ilike(q),
                Agent.job_title.ilike(q),
                Agent.phone.ilike(q)
            )
        )

    result = await db.execute(stmt)
    agents = result.scalars().all()

    return [
        {
            "id": str(a.id),
            "agent_code": a.agent_code,
            "name": a.name,
            "phone": a.phone,
            "channel": a.channel or "-",
            "district": a.district or "-",
            "branch_office": a.branch_office or "-",
            "job_title": a.job_title or "-",
            "line_user_id": a.line_user_id,
            "is_verified": a.is_verified,
            "status": a.status,
            "is_bound_real_line": bool(a.line_user_id and not a.line_user_id.startswith("U_MOCK")),
            "created_at": a.created_at.isoformat() if a.created_at else None
        }
        for a in agents
    ]


@router.post("")
async def create_agent(payload: AgentCreate, db: AsyncSession = Depends(get_db)):
    """新增業務員"""
    res = await db.execute(select(Agent).where(Agent.agent_code == payload.agent_code))
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"工號 '{payload.agent_code}' 已存在！")

    agent = Agent(
        agent_code=payload.agent_code,
        name=payload.name,
        phone=payload.phone,
        channel=payload.channel,
        district=payload.district,
        branch_office=payload.branch_office,
        job_title=payload.job_title,
        status="active"
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return {"status": "success", "agent_id": str(agent.id), "agent_code": agent.agent_code}


@router.post("/batch-import-excel")
async def batch_import_agents_excel(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """
    Excel 批次匯入與更新業務員主資料
    - 標頭欄位需求：工號 (必填), 姓名 (必填), 手機號碼 (必填)；選填：銷售通路, 督導區, 通訊處, 職級, 帳號狀態
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

    code_col_idx = None
    for c in ["工號", "agent_code", "業務員工號"]:
        if c in header_map:
            code_col_idx = header_map[c]
            break

    name_col_idx = None
    for c in ["姓名", "name", "業務員姓名"]:
        if c in header_map:
            name_col_idx = header_map[c]
            break

    phone_col_idx = None
    for c in ["手機號碼", "phone", "手機"]:
        if c in header_map:
            phone_col_idx = header_map[c]
            break

    if code_col_idx is None or name_col_idx is None or phone_col_idx is None:
        raise HTTPException(status_code=400, detail="Excel 缺少必要標頭：必須包含 '工號', '姓名' 與 '手機號碼'")

    channel_col_idx = None
    for c in ["銷售通路", "channel", "通路"]:
        if c in header_map:
            channel_col_idx = header_map[c]
            break

    district_col_idx = None
    for c in ["督導區", "區部", "督導區/區部", "district"]:
        if c in header_map:
            district_col_idx = header_map[c]
            break

    branch_col_idx = None
    for c in ["通訊處", "單位", "branch_office", "通訊處/單位"]:
        if c in header_map:
            branch_col_idx = header_map[c]
            break

    job_col_idx = None
    for c in ["職級", "job_title"]:
        if c in header_map:
            job_col_idx = header_map[c]
            break

    status_col_idx = None
    for c in ["帳號狀態", "狀態", "status"]:
        if c in header_map:
            status_col_idx = header_map[c]
            break

    def get_val(row_data, idx):
        if idx is None or idx >= len(row_data):
            return None
        val = row_data[idx]
        if val is None:
            return None
        s = str(val).strip()
        return s if s != "" else None

    created_count = 0
    updated_count = 0

    for row in rows[1:]:
        code = get_val(row, code_col_idx) or ""
        name = get_val(row, name_col_idx) or ""
        phone = get_val(row, phone_col_idx) or ""

        if not code or not name or not phone:
            continue

        channel = get_val(row, channel_col_idx)
        district = get_val(row, district_col_idx)
        branch = get_val(row, branch_col_idx)
        job = get_val(row, job_col_idx)

        st_val = get_val(row, status_col_idx) or "active"
        if "離職" in st_val or st_val == "resigned":
            st_val = "resigned"
        elif "停權" in st_val or st_val == "suspended":
            st_val = "suspended"
        else:
            st_val = "active"

        res = await db.execute(select(Agent).where(Agent.agent_code == code))
        agent = res.scalar_one_or_none()

        if agent:
            agent.name = name
            agent.phone = phone
            if channel: agent.channel = channel
            if district: agent.district = district
            if branch: agent.branch_office = branch
            if job: agent.job_title = job
            agent.status = st_val
            updated_count += 1
        else:
            agent = Agent(
                agent_code=code,
                name=name,
                phone=phone,
                channel=channel or "直營",
                district=district or "台北督導區",
                branch_office=branch or "台北一處",
                job_title=job or "區經理",
                status=st_val
            )
            db.add(agent)
            created_count += 1

    await db.commit()
    return {
        "created_count": created_count,
        "updated_count": updated_count,
        "message": f"業務員主檔匯入完成！成功新增 {created_count} 筆，更新 {updated_count} 筆。"
    }


@router.put("/{agent_id}")
async def update_agent(agent_id: str, payload: AgentUpdate, db: AsyncSession = Depends(get_db)):
    """更新業務員主資料 (換單位、晉升、降職、狀態變更)"""
    try:
        uid = uuid.UUID(agent_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="無效的 agent_id")

    res = await db.execute(select(Agent).where(Agent.id == uid))
    agent = res.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="查無此業務員")

    if payload.name is not None:
        agent.name = payload.name
    if payload.phone is not None:
        agent.phone = payload.phone
    if payload.channel is not None:
        agent.channel = payload.channel
    if payload.district is not None:
        agent.district = payload.district
    if payload.branch_office is not None:
        agent.branch_office = payload.branch_office
    if payload.job_title is not None:
        agent.job_title = payload.job_title
    if payload.status is not None:
        agent.status = payload.status

    await db.commit()
    return {"status": "success", "message": f"業務員 {agent.agent_code} 資料已更新！"}


@router.post("/{agent_id}/offboard")
async def offboard_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """辦理業務員離職 (標記為 resigned 並強制清除 LINE 身分綁定)"""
    try:
        uid = uuid.UUID(agent_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="無效的 agent_id")

    res = await db.execute(select(Agent).where(Agent.id == uid))
    agent = res.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="查無此業務員")

    agent.status = "resigned"
    agent.line_user_id = None
    agent.is_verified = False

    await db.commit()
    return {"status": "success", "message": f"業務員 {agent.agent_code} ({agent.name}) 已成功辦理離職並撤銷 LINE 權限！"}


@router.post("/{agent_id}/unbind")
async def unbind_agent_line(agent_id: str, db: AsyncSession = Depends(get_db)):
    """解除業務員 LINE 綁定"""
    try:
        uid = uuid.UUID(agent_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="無效的 agent_id")

    res = await db.execute(select(Agent).where(Agent.id == uid))
    agent = res.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="查無此業務員")

    agent.line_user_id = None
    agent.is_verified = False

    await db.commit()
    return {"status": "success", "message": f"業務員 {agent.agent_code} 的 LINE 帳號已解綁！"}


@router.delete("/{agent_id}")
async def delete_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """刪除業務員紀錄"""
    try:
        uid = uuid.UUID(agent_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="無效的 agent_id")

    res = await db.execute(select(Agent).where(Agent.id == uid))
    agent = res.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="查無此業務員")

    await db.delete(agent)
    await db.commit()
    return {"status": "success", "message": f"業務員 {agent.agent_code} ({agent.name}) 已刪除"}

