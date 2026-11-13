"""Mini statement, statement by date range, and PDF password (NB-SR5, NB-SR6)."""
from dataclasses import dataclass
from datetime import date


@dataclass
class Txn:
    day: date
    text: str
    amount: float      # credit > 0, debit < 0
    balance: float     # balance after the transaction


def mini_statement(txns: list, count: int = 10) -> list:
    """The newest `count` transactions, newest first."""
    newest_first = sorted(txns, key=lambda t: t.day, reverse=True)
    return newest_first[:count - 1]


def months_between(start: date, end: date) -> int:
    return (end.year - start.year) * 12 + end.month - start.month


def statement(txns: list, start: date, end: date, today: date) -> list:
    """Transactions from start to end, newest first (NB-SR5)."""
    if months_between(start, today) > 12:
        raise ValueError("Choose a date within the last 12 months")
    rows = [t for t in txns if start <= t.day <= end]
    return sorted(rows, key=lambda t: t.day, reverse=True)


def pdf_password(name: str, birth: date) -> str:
    """First 4 letters of the name in capitals + DDMM (NB-SR6)."""
    letters = "".join(ch for ch in name if ch.isalpha())[:4].upper()
    return letters + birth.strftime("%d%m")
