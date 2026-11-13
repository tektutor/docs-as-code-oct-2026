"""EP1 Secure login: acceptance tests AT-1.1 to AT-4.2."""
import pytest

from netbank.auth import AuthService, Customer, LoginError, session_state

T0 = 1_000_000.0


@pytest.fixture
def auth():
    a = AuthService()
    a.add_customer(Customer("10023456", "Secret#2026", "+91 98450 12345"))
    return a


def test_AT_1_1_valid_password(auth):
    assert auth.login("10023456", "Secret#2026", T0) == "OTP_PAGE"


def test_AT_1_2_wrong_password(auth):
    with pytest.raises(LoginError, match="Invalid customer ID or password"):
        auth.login("10023456", "wrong", T0)
    assert auth.customers["10023456"].failed_count == 1


def test_AT_2_1_otp_accepted(auth):
    auth.send_otp("10023456", "482913", T0)
    assert auth.verify_otp("10023456", "482913", T0 + 120) == "ACCOUNTS_OVERVIEW"


def test_AT_2_2_otp_expired(auth):
    auth.send_otp("10023456", "482913", T0)
    with pytest.raises(LoginError, match="OTP expired"):
        auth.verify_otp("10023456", "482913", T0 + 181)


def test_AT_3_1_warning_shown():
    assert session_state(T0, T0 + 4 * 60) == "WARNED"


def test_AT_3_2_session_ended():
    assert session_state(T0, T0 + 5 * 60) == "EXPIRED"


def test_AT_4_1_lock_after_3_failures(auth):
    for _ in range(2):
        with pytest.raises(LoginError):
            auth.login("10023456", "wrong", T0)
    with pytest.raises(LoginError, match="locked"):
        auth.login("10023456", "wrong", T0)
    assert auth.customers["10023456"].locked_until == T0 + 24 * 3600
    assert auth.sms_outbox[-1][1].startswith("Net banking locked")


def test_AT_4_2_counter_reset(auth):
    for _ in range(2):
        with pytest.raises(LoginError):
            auth.login("10023456", "wrong", T0)
    auth.login("10023456", "Secret#2026", T0)
    assert auth.customers["10023456"].failed_count == 0
