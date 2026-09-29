import pytest
import pandas as pd
from io import BytesIO
from app.services.excel_service import ExcelNotificationImportService


def test_excel_parse_valid():
    data = {
        "工號": ["A001", "A002"],
        "通知類別": ["行政照會", "商品異動"],
        "通知標題": ["照會單補件", "停售通知"],
        "原始內文": ["客戶：張大明 身分證：A123456789 請補件", "商品 LIFE01 即將停售"]
    }
    df = pd.DataFrame(data)
    out = BytesIO()
    df.to_excel(out, index=False)
    bytes_data = out.getvalue()

    valid_items, errors = ExcelNotificationImportService.process_excel_bytes(bytes_data)

    assert len(errors) == 0
    assert len(valid_items) == 2
    assert "張*明" in valid_items[0]["masked_content"]
    assert "A12****789" in valid_items[0]["masked_content"]


def test_excel_parse_invalid_category():
    data = {
        "工號": ["A001"],
        "通知類別": ["無效類別"],
        "通知標題": ["標題"],
        "原始內文": ["內文"]
    }
    df = pd.DataFrame(data)
    out = BytesIO()
    df.to_excel(out, index=False)
    bytes_data = out.getvalue()

    valid_items, errors = ExcelNotificationImportService.process_excel_bytes(bytes_data)

    assert len(errors) == 1
    assert "無效類別" in errors[0]
