from datetime import date
from decimal import Decimal

from app.modules.budget_constructor.parsing import kcsr_slice, normalize_code, parse_date, parse_money


def test_normalize_budget_codes_and_kcsr_segments():
    assert normalize_code("13.2.02.61052") == "1320261052"
    assert normalize_code("101016105Б") == "101016105Б"
    assert kcsr_slice("13.2.02.61052", 6, 4) == "6105"
    assert kcsr_slice("08.3.02.97070", 6, 3) == "970"
    assert kcsr_slice(None, 6, 4) is None


def test_parse_money_accepts_ru_and_machine_formats():
    assert parse_money("44 622 636,12") == Decimal("44622636.12")
    assert parse_money("118776000.00") == Decimal("118776000.00")
    assert parse_money("") == Decimal("0.00")
    assert parse_money(None) == Decimal("0.00")


def test_parse_date_accepts_source_formats():
    assert parse_date("20.08.2025") == date(2025, 8, 20)
    assert parse_date("2025-10-17 00:00:00.000") == date(2025, 10, 17)
    assert parse_date("2026-04-01") == date(2026, 4, 1)
    assert parse_date("") is None
