import pytest
from app.services.masking_service import DataMaskingService


def test_mask_chinese_name():
    assert DataMaskingService.mask_name("張三") == "張*"
    assert DataMaskingService.mask_name("張大明") == "張*明"
    assert DataMaskingService.mask_name("歐陽六六") == "歐**六"


def test_mask_english_name():
    assert DataMaskingService.mask_name("John Smith") == "J*** S****"


def test_mask_tw_id():
    assert DataMaskingService.mask_tw_id("A123456789") == "A12****789"
    assert DataMaskingService.mask_tw_id("B220011223") == "B22****223"


def test_mask_policy_number():
    assert DataMaskingService.mask_policy_number("P987654321") == "P98****321"


def test_sanitize_full_text():
    raw_text = "照會通知：客戶：張大明，身分證：A123456789，保單號碼：P987654321 需要補件。"
    sanitized = DataMaskingService.sanitize_text(raw_text)

    assert "張大明" not in sanitized
    assert "張*明" in sanitized
    assert "A123456789" not in sanitized
    assert "A12****789" in sanitized
    assert "P987654321" not in sanitized
    assert "P98****321" in sanitized
