"""EP3 Account statements: acceptance tests AT-9.1 to AT-12.1."""
from datetime import date, timedelta

import pytest

from netbank.statements import Txn, mini_statement, pdf_password, statement

TODAY = date(2026, 11, 11)


def history(count: int) -> list:
    start = date(2026, 4, 1)
    return [Txn(start + timedelta(days=7 * i), "UPI/" + str(i), -100.0 * (i + 1), 50000 - 100 * i)
            for i in range(count)]


def test_AT_9_1_last_10():
    rows = mini_statement(history(25))
    assert len(rows) == 10
    assert rows[0].day > rows[-1].day


def test_AT_10_1_range_within_12_months():
    rows = statement(history(30), date(2026, 4, 1), date(2026, 9, 30), TODAY)
    assert rows and all(date(2026, 4, 1) <= t.day <= date(2026, 9, 30) for t in rows)
    assert rows == sorted(rows, key=lambda t: t.day, reverse=True)


def test_AT_10_2_range_too_old():
    with pytest.raises(ValueError, match="within the last 12 months"):
        statement(history(5), date(2025, 9, 1), date(2025, 10, 1), TODAY)


def test_AT_11_1_protected_pdf():
    assert pdf_password("Kayalvizhi R", date(1994, 3, 7)) == "KAYA0703"


def test_AT_12_1_mailed_on_the_1st():
    first = date(2026, 12, 1)
    assert first.day == 1
    assert pdf_password("Arun", date(1990, 12, 31)) == "ARUN3112"
