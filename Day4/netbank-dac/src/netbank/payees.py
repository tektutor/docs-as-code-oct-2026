"""Beneficiaries, bill payment, and debit alerts (NB-SR7, NB-SR11, NB-SR12)."""
from dataclasses import dataclass

KNOWN_IFSC = {"SBIN0001234": "State Bank of India, Pune",
              "HDFC0000123": "HDFC Bank, Hosur"}


@dataclass
class Payee:
    name: str
    account: str
    ifsc: str
    added_at: float
    sent_in_cooling: float = 0.0
    pending: int = 0
    deleted: bool = False


class PayeeError(Exception):
    """Raised with the message the customer sees."""


def add_payee(payees: list, name: str, account: str, account_again: str,
              ifsc: str, otp_ok: bool, now: float) -> Payee:
    if account != account_again:
        raise PayeeError("Account numbers do not match")
    if ifsc not in KNOWN_IFSC:
        raise PayeeError("Unknown IFSC code")
    if not otp_ok:
        raise PayeeError("Wrong OTP")
    p = Payee(name, account, ifsc, added_at=now)
    payees.append(p)
    return p


def delete_payee(payees: list, payee: Payee) -> None:
    if payee.pending:
        raise PayeeError("Wait for the pending transfer to finish")
    payee.deleted = True          # soft delete, kept for audit


def visible(payees: list) -> list:
    return [p for p in payees if not p.deleted]


def pay_bill(account, consumer_no: str, bills: dict) -> str:
    amount = bills[consumer_no]
    if account.balance < amount:
        raise PayeeError("Insufficient balance")
    account.balance -= amount
    del bills[consumer_no]
    return "Receipt BBPS-" + consumer_no


def debit_alert(amount: float, account_no: str, balance: float, posted_at: float) -> dict:
    """SMS and e-mail text for one debit, due within 60 seconds (NB-SR12)."""
    text = "INR {:,.2f} debited from A/c XX{}. Available balance INR {:,.2f}.".format(
        amount, account_no[-4:], balance)
    return {"sms": text, "email": text, "send_by": posted_at + 60}
