"""Own-account, IMPS, NEFT, and RTGS transfers with limits (NB-SR7 to NB-SR11)."""

IMPS_MAX = 500_000          # NB-SR8: INR 5,00,000 per IMPS transfer
RTGS_MIN = 200_000          # NB-SR9: RTGS from INR 2,00,000
DAILY_LIMIT = 1_000_000     # NB-SR10: default daily third-party limit
COOLING_CAP = 50_000        # NB-SR11: first 24 hours after adding a payee
COOLING_SECONDS = 24 * 3600


class TransferError(Exception):
    """Raised with the message the customer sees."""


_next_ref = [7780]


def _reference() -> str:
    _next_ref[0] += 1
    return str(_next_ref[0])


def own_transfer(source, target, amount: float) -> str:
    """Move money between two accounts of one customer (NB-SR7)."""
    if amount <= 0:
        raise TransferError("Enter an amount above zero")
    if source.balance < amount:
        raise TransferError("Insufficient balance")
    source.balance -= amount
    target.balance += amount
    return _reference()


def check_daily_limit(sent_today: float, amount: float, limit: float = DAILY_LIMIT) -> None:
    if sent_today + amount > limit:
        raise TransferError("Daily limit exceeded")


def check_cooling(payee, amount: float, now: float) -> None:
    if now - payee.added_at < COOLING_SECONDS and payee.sent_in_cooling + amount > COOLING_CAP:
        raise TransferError("New payee limit is INR 50,000 for the first 24 hours")


def third_party_transfer(mode: str, payee, amount: float, sent_today: float,
                         otp_ok: bool, now: float) -> dict:
    """IMPS, NEFT, or RTGS to a registered payee (NB-SR8, NB-SR9)."""
    if mode == "IMPS" and amount > IMPS_MAX:
        raise TransferError("IMPS limit is INR 5,00,000")
    if mode == "RTGS" and amount < RTGS_MIN:
        raise TransferError("RTGS needs at least INR 2,00,000")
    check_daily_limit(sent_today, amount)
    check_cooling(payee, amount, now)
    if not otp_ok:
        return {"status": "FAILED", "reason": "OTP wrong"}
    payee.sent_in_cooling += amount
    return {"status": "SUCCESS", "reference": mode + _reference(), "seconds": 4}
