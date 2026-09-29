import openpyxl
from io import BytesIO
from typing import List, Dict, Any, Tuple
from app.services.masking_service import DataMaskingService


class ExcelNotificationImportService:
    """
    Excel 批次匯入發送個別通知 - 防呆校驗引擎 (支援通路 >> 督導區 >> 通訊處 >> 職級 分眾標籤比對)
    - 必要欄位：工號, 通知類別, 通知標題, 原始內文
    - 選填分眾欄位：督導區, 通訊處, 職級 (可用於分眾標籤比對與防呆)
    """
    REQUIRED_COLUMNS = ["工號", "通知類別", "通知標題", "原始內文"]
    ALLOWED_CATEGORIES = ["行政照會", "商品異動", "營運活動"]

    @classmethod
    def process_excel_bytes(cls, file_bytes: bytes) -> Tuple[List[Dict[str, Any]], List[str]]:
        errors: List[str] = []
        valid_items: List[Dict[str, Any]] = []

        try:
            wb = openpyxl.load_workbook(BytesIO(file_bytes), data_only=True)
            ws = wb.active
        except Exception as e:
            return [], [f"Excel 檔案無法解析，請確認檔案格式是否正確: {str(e)}"]

        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            return [], ["Excel 檔案沒有數據"]

        headers = [str(cell).strip() if cell is not None else "" for cell in rows[0]]
        header_map = {name: idx for idx, name in enumerate(headers)}

        missing_cols = [col for col in cls.REQUIRED_COLUMNS if col not in header_map]
        if missing_cols:
            return [], [f"Excel 缺少必要標頭欄位: {', '.join(missing_cols)}"]

        has_district_tag = "督導區" in header_map or "區部" in header_map
        district_col_idx = header_map.get("督導區", header_map.get("區部"))

        has_branch_tag = "通訊處" in header_map or "單位" in header_map
        branch_col_idx = header_map.get("通訊處", header_map.get("單位"))

        has_job_tag = "職級" in header_map
        job_col_idx = header_map.get("職級")

        def get_val(row_data, col_idx):
            if col_idx is None or col_idx >= len(row_data):
                return None
            val = row_data[col_idx]
            if val is None:
                return None
            val_str = str(val).strip()
            return val_str if val_str != "" else None

        for idx, row in enumerate(rows[1:], start=2):
            agent_code = get_val(row, header_map.get("工號")) or ""
            category = get_val(row, header_map.get("通知類別")) or ""
            title = get_val(row, header_map.get("通知標題")) or ""
            raw_content = get_val(row, header_map.get("原始內文")) or ""

            district_tag = get_val(row, district_col_idx) if has_district_tag else None
            branch_tag = get_val(row, branch_col_idx) if has_branch_tag else None
            job_tag = get_val(row, job_col_idx) if has_job_tag else None

            if not agent_code:
                errors.append(f"第 {idx} 行：工號不可為空")
                continue
            if category not in cls.ALLOWED_CATEGORIES:
                errors.append(f"第 {idx} 行：通知類別 '{category}' 無效，必須為 {cls.ALLOWED_CATEGORIES}")
                continue
            if not title:
                errors.append(f"第 {idx} 行：通知標題不可為空")
                continue
            if not raw_content:
                errors.append(f"第 {idx} 行：原始內文不可為空")
                continue

            masked_content = DataMaskingService.sanitize_text(raw_content)

            valid_items.append({
                "row_num": idx,
                "agent_code": agent_code,
                "district_tag": district_tag,
                "branch_tag": branch_tag,
                "job_tag": job_tag,
                "category": category,
                "title": title,
                "raw_content": raw_content,
                "masked_content": masked_content
            })

        return valid_items, errors

