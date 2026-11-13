"""EP4 Fund transfer: acceptance tests AT-13.1 to AT-16.1."""
import pytest

from netbank.accounts import Current, Savings
from netbank.payees import Payee
from netbank.transfers import TransferError, own_transfer, third_party_transfer

DAY = 24 * 3600
NOW = 10 * DAY


def old_payee():
    return Payee("Arun Kumar", "33120045678", "SBIN0001234", added_at=NOW - 3 * DAY)


def test_AT_13_1_instant_transfer():
    s, c = Savings("50300099009012", 50000), Current("50200088005678", 0)
    ref = own_transfer(s, c, 10000)
    assert (s.balance, c.balance) == (40000, 10000)
    assert ref.isdigit()


def test_AT_13_2_insufficient_balance():
    s, c = Savings("50300099009012", 5000), Current("50200088005678", 0)
    with pytest.raises(TransferError, match="Insufficient balance"):
        own_transfer(s, c, 10000)
    assert (s.balance, c.balance) == (5000, 0)


def test_AT_14_1_imps_success():
    r = third_party_transfer("IMPS", old_payee(), 20000, sent_today=0, otp_ok=True, now=NOW)
    assert r["status"] == "SUCCESS" and r["reference"].startswith("IMPS")
    assert r["seconds"] <= 30


def test_AT_14_2_above_imps_limit():
    with pytest.raises(TransferError, match="IMPS limit is INR 5,00,000"):
        third_party_transfer("IMPS", old_payee(), 600000, sent_today=0, otp_ok=True, now=NOW)


def test_AT_15_1_rtgs_minimum():
    with pytest.raises(TransferError, match="RTGS needs at least INR 2,00,000"):
        third_party_transfer("RTGS", old_payee(), 150000, sent_today=0, otp_ok=True, now=NOW)


def test_AT_16_1_limit_reached():
    with pytest.raises(TransferError, match="Daily limit exceeded"):
        third_party_transfer("NEFT", old_payee(), 100000, sent_today=950000, otp_ok=True, now=NOW)
