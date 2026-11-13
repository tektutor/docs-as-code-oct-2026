"""Login, OTP, lockout, and session rules (NB-SR1, NB-SR2, NB-SR3)."""
from dataclasses import dataclass, field

OTP_VALID_SECONDS = 180          # NB-SR1: OTP expires after 3 minutes
MAX_FAILURES = 3                 # NB-SR3: lock after 3 failed passwords
LOCK_SECONDS = 24 * 3600         # NB-SR3: lock for 24 hours
WARN_AFTER_SECONDS = 240         # NB-SR2: warn 60 seconds before the end
IDLE_LIMIT_SECONDS = 300         # NB-SR2: end the session after 5 idle minutes


class LoginError(Exception):
    """Raised with the message the customer sees."""


@dataclass
class Customer:
    customer_id: str
    password: str
    mobile: str
    failed_count: int = 0
    locked_until: float = 0.0


@dataclass
class AuthService:
    customers: dict = field(default_factory=dict)
    sms_outbox: list = field(default_factory=list)
    otps: dict = field(default_factory=dict)

    def add_customer(self, customer: Customer) -> None:
        self.customers[customer.customer_id] = customer

    def login(self, customer_id: str, password: str, now: float) -> str:
        """Check the password. Returns the next page: 'OTP_PAGE'."""
        c = self.customers.get(customer_id)
        if c is None:
            raise LoginError("Invalid customer ID or password")
        if c.locked_until > now:
            raise LoginError("Net banking is locked. Try again after 24 hours.")
        if c.password != password:
            c.failed_count += 1
            if c.failed_count >= MAX_FAILURES:
                c.locked_until = now + LOCK_SECONDS
                self.sms_outbox.append((c.mobile, "Net banking locked after 3 failed logins"))
                raise LoginError("Net banking is locked. Try again after 24 hours.")
            raise LoginError("Invalid customer ID or password")
        c.failed_count = 0
        return "OTP_PAGE"

    def send_otp(self, customer_id: str, otp: str, now: float) -> None:
        c = self.customers[customer_id]
        self.otps[customer_id] = (otp, now)
        self.sms_outbox.append((c.mobile, "Your NetBank OTP is " + otp))

    def verify_otp(self, customer_id: str, otp: str, now: float) -> str:
        """Returns 'ACCOUNTS_OVERVIEW' or raises LoginError."""
        sent, at = self.otps[customer_id]
        if now - at > OTP_VALID_SECONDS:
            raise LoginError("OTP expired")
        if otp != sent:
            raise LoginError("Wrong OTP")
        return "ACCOUNTS_OVERVIEW"


def session_state(last_activity: float, now: float) -> str:
    """ACTIVE, WARNED, or EXPIRED after idle time (NB-SR2)."""
    idle = now - last_activity
    if idle >= IDLE_LIMIT_SECONDS:
        return "EXPIRED"
    if idle >= WARN_AFTER_SECONDS:
        return "WARNED"
    return "ACTIVE"
