"""EP5 Beneficiaries and EP6 Bills and alerts: AT-17.1 to AT-20.1."""
import pytest

from netbank.accounts import Savings
from netbank.payees import PayeeError, add_payee, debit_alert, delete_payee, pay_bill, visible
from netbank.transfers import TransferError, third_party_transfer

NOW = 1_000_000.0


def test_AT_17_1_valid_ifsc():
    payees = []
    p = add_payee(payees, "Arun Kumar", "33120045678", "33120045678", "SBIN0001234", True, NOW)
    assert p in payees
    third_party_transfer("IMPS", p, 50000, sent_today=0, otp_ok=True, now=NOW + 60)
    with pytest.raises(TransferError, match="first 24 hours"):
        third_party_transfer("IMPS", p, 1, sent_today=50000, otp_ok=True, now=NOW + 120)


def test_AT_17_2_unknown_ifsc():
    with pytest.raises(PayeeError, match="Unknown IFSC code"):
        add_payee([], "Arun Kumar", "33120045678", "33120045678", "ABCD0000000", True, NOW)


def test_AT_18_1_deleted():
    payees = []
    p = add_payee(payees, "Arun Kumar", "33120045678", "33120045678", "SBIN0001234", True, NOW)
    delete_payee(payees, p)
    assert visible(payees) == []


def test_AT_19_1_bill_paid():
    acc = Savings("50300099009012", 10000)
    bills = {"123456789": 2340}
    assert pay_bill(acc, "123456789", bills) == "Receipt BBPS-123456789"
    assert acc.balance == 7660 and bills == {}


def test_AT_20_1_sms_within_60_s():
    a = debit_alert(10000, "50300099009012", 74250.50, posted_at=NOW)
    assert "INR 10,000.00 debited from A/c XX9012" in a["sms"]
    assert "74,250.50" in a["email"]
    assert a["send_by"] - NOW <= 60
