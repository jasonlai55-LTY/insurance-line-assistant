from io import BytesIO
from fastapi import APIRouter, HTTPException, Response
from urllib.parse import quote
import openpyxl

router = APIRouter(prefix="/admin/templates", tags=["CMS Excel Templates"])


def create_excel_bytes(data: list) -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active

    if not data:
        buffer = BytesIO()
        wb.save(buffer)
        return buffer.getvalue()

    headers = list(data[0].keys())
    ws.append(headers)

    for item in data:
        row = [item.get(h, "") for h in headers]
        ws.append(row)

    buffer = BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


@router.get("/{template_type}")
def download_excel_template(template_type: str):
    """
    動態下載各功能對應之標準 Excel 空白/示範範本檔
    - push: 個案照會批次推播
    - tags: 業務員分眾標籤
    - assets: 素材與規範表單
    - agents: 業務員主資料與異動
    """
    if template_type == "push":
        data = [
            {
                "工號": "A001",
                "通知類別": "行政照會",
                "通知標題": "投保照會通知範例",
                "原始內文": "保戶 A123456789 請於 3 日內補齊親簽聲明書",
                "督導區": "台北督導區",
                "通訊處": "台北一處",
                "職級": "區經理"
            }
        ]
        filename = "個案照會批次推播範本.xlsx"
    elif template_type == "tags":
        data = [
            {"標籤名稱": "區主任 (TS)", "標籤分類": "職級"},
            {"標籤名稱": "台北督導區", "標籤分類": "督導區"},
            {"標籤名稱": "新竹分公司", "標籤分類": "通訊處"},
            {"標籤名稱": "保經代通路", "標籤分類": "通路"}
        ]
        filename = "業務員分眾標籤範本.xlsx"
    elif template_type == "assets":
        data = [
            {
                "商品代號": "ACC01",
                "素材標題": "新意外險專案銷售手冊",
                "類別": "商品素材",
                "檔案網址": "https://example.com/dm.pdf",
                "內部權限": "否"
            }
        ]
        filename = "素材與規範表單範本.xlsx"
    elif template_type == "agents":
        data = [
            {
                "工號": "A002",
                "姓名": "林小明",
                "手機號碼": "0987654321",
                "銷售通路": "直營",
                "督導區": "台中區部",
                "通訊處": "台中分公司",
                "職級": "處經理",
                "帳號狀態": "在職"
            }
        ]
        filename = "業務員主資料匯入範本.xlsx"
    else:
        raise HTTPException(status_code=400, detail="未知的範本類型")

    excel_bytes = create_excel_bytes(data)
    encoded_filename = quote(filename)
    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
    }

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )
