"""Savings, Current, and Personal loan accounts (NB-SR4)."""
from dataclasses import dataclass, field
from datetime import date


@dataclass
class Account:
    number: str
    balance: float

    @property
    def masked_number(self) -> str:
        return "XXXX" + self.number[-4:]


@dataclass
class Savings(Account):
    interest_rate: float = 3.0
    nominee: str = ""
    ifsc: str = ""
    branch: str = ""
    kind: str = "Savings"

    def details(self) -> dict:
        masked = self.nominee[:1] + "*" * (len(self.nominee) - 1) if self.nominee else ""
        return {"interest_rate": self.interest_rate, "nominee": masked,
                "ifsc": self.ifsc, "branch": self.branch}


@dataclass
class Current(Account):
    od_limit: float = 0.0
    od_used: float = 0.0
    kind: str = "Current"

    def available(self) -> float:
        return self.balance + self.od_limit - self.od_used


@dataclass
class PersonalLoan(Account):
    emi: float = 0.0
    due_dates: list = field(default_factory=list)   # unpaid EMI due dates
    kind: str = "Personal loan"

    def next_due(self, today: date) -> date:
        return min(d for d in self.due_dates if d >= today)

    def remaining_emis(self) -> int:
        return len(self.due_dates)


ORDER = {"Savings": 0, "Current": 1, "Personal loan": 2}


def overview(accounts: list) -> list:
    """One row per account: deposits first, loans last (NB-SR4)."""
    rows = [(a.kind, a.masked_number, a.balance) for a in accounts]
    return sorted(rows, key=lambda r: ORDER[r[0]])
