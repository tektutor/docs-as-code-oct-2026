"""EP2 Accounts overview: acceptance tests AT-5.1 to AT-8.1."""
from datetime import date

from netbank.accounts import Current, PersonalLoan, Savings, overview


def test_AT_5_1_three_account_types():
    rows = overview([
        PersonalLoan("50100077001234", -350000, emi=12500),
        Current("50200088005678", 125000),
        Savings("50300099009012", 84250.50),
    ])
    assert [r[0] for r in rows] == ["Savings", "Current", "Personal loan"]
    assert rows[0] == ("Savings", "XXXX9012", 84250.50)


def test_AT_6_1_savings_details_shown():
    s = Savings("50300099009012", 84250.50, interest_rate=3.0, nominee="Meena",
                ifsc="SBIN0001234", branch="Pune Main")
    d = s.details()
    assert d == {"interest_rate": 3.0, "nominee": "M****",
                 "ifsc": "SBIN0001234", "branch": "Pune Main"}


def test_AT_7_1_overdraft_shown():
    c = Current("50200088005678", 50000, od_limit=200000, od_used=30000)
    assert c.available() == 220000


def test_AT_8_1_loan_shown():
    loan = PersonalLoan("50100077001234", -350000, emi=12500,
                        due_dates=[date(2026, 12, 5), date(2027, 1, 5), date(2027, 2, 5)])
    assert loan.emi == 12500
    assert loan.next_due(date(2026, 11, 11)) == date(2026, 12, 5)
    assert loan.remaining_emis() == 3
