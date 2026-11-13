"""NetBank demo web application for manual testing.

    python3 app.py            then open http://localhost:8000
    python3 app.py 8080       on another port

It uses only the Python standard library and the rules in src/netbank, the
same code the pytest acceptance tests check. A bug in src/netbank shows up
here too, for example the mini statement with 9 rows (AT-9.1).

Demo login:   customer ID 10023456, password Secret#2026
There is no real SMS: OTPs and alerts appear in the box "Demo phone".
The "Demo clock" buttons move the time forward, so you can test the OTP
expiry (3 minutes), the session timeout (5 minutes), the lockout (24 hours),
and the beneficiary cooling period (24 hours) without waiting.
Everything is kept in memory. "Reset demo data" starts again.
"""
import html
import os
import secrets
import sys
import time
from datetime import date, datetime, timedelta
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))

from netbank.accounts import Current, PersonalLoan, Savings, overview  # noqa: E402
from netbank.auth import (AuthService, Customer, LoginError,  # noqa: E402
                          WARN_AFTER_SECONDS, IDLE_LIMIT_SECONDS, session_state)
from netbank.payees import (KNOWN_IFSC, PayeeError, add_payee, debit_alert,  # noqa: E402
                            delete_payee, pay_bill, visible)
from netbank.statements import Txn, mini_statement, pdf_password, statement  # noqa: E402
from netbank.transfers import TransferError, own_transfer, third_party_transfer  # noqa: E402

CUSTOMER_ID, PASSWORD = "10023456", "Secret#2026"
NAME, BIRTH = "Arun Kumar", date(1988, 3, 15)


# ----------------------------------------------------------------- demo data
class Bank:
    """All demo state. reset() puts it back to the start."""

    def reset(self):
        self.offset = 0.0                      # seconds added by the demo clock
        self.auth = AuthService()
        self.auth.add_customer(Customer(CUSTOMER_ID, PASSWORD, "+91 98450 12345"))
        self.sessions = {}                     # sid -> {"cid", "last", "otp_tries", "state"}
        self.pending = {}                      # sid -> waiting third-party action
        self.phone = []                        # (time text, message)
        self.savings = Savings("50300099009012", 50000.0, interest_rate=3.0, nominee="Meena",
                               ifsc="SBIN0001234", branch="Pune Main")
        self.current = Current("50200088005678", 520000.0, od_limit=200000, od_used=30000)
        first = date(2026, 12, 5)
        self.loan = PersonalLoan("50100077001234", -345000.0, emi=12500,
                                 due_dates=[_add_months(first, i) for i in range(28)])
        self.accounts = [self.loan, self.current, self.savings]
        self.txns = {self.savings.number: _history(), self.current.number: [], self.loan.number: []}
        self.payees = []
        self.sent_today = {}                   # date -> third-party total
        self.bills = {"123456789": 2340.0}

    def now(self):
        return time.time() + self.offset

    def today(self):
        return datetime.fromtimestamp(self.now()).date()

    def account(self, number):
        return next(a for a in self.accounts if a.number == number)

    def post(self, account, text, amount):
        """Change the balance, then book the transaction."""
        account.balance += amount
        self.book(account, text, amount)

    def book(self, account, text, amount):
        """Record a transaction whose balance change is already made; alert on debits (NB-SR12)."""
        self.txns[account.number].append(Txn(self.today(), text, amount, account.balance))
        if amount < 0:
            alert = debit_alert(-amount, account.number, account.balance, self.now())
            self.sms(alert["sms"])

    def drain_sms(self):
        """Copy the SMS that the auth rules sent (OTP, lockout) to the demo phone."""
        while self.auth.sms_outbox:
            self.sms(self.auth.sms_outbox.pop(0)[1])

    def sms(self, text):
        self.phone.insert(0, (datetime.fromtimestamp(self.now()).strftime("%d %b %H:%M"), text))


def _add_months(d, n):
    m = d.month - 1 + n
    return date(d.year + m // 12, m % 12 + 1, d.day)


def _history():
    """40 Savings transactions from January to October 2026, 7 days apart."""
    rows, balance = [], 50000.0 + 40 * 150
    for i in range(40):
        day = date(2026, 1, 10) + timedelta(days=7 * i)
        amount = 25000.0 if i % 10 == 0 else -(300.0 + 37 * i)
        text = "SALARY TEKTUTOR" if amount > 0 else "UPI/%06d/GROCERY" % (410000 + i)
        balance += amount
        rows.append(Txn(day, text, amount, balance))
    # make the last balance equal the account balance
    shift = 50000.0 - rows[-1].balance
    return [Txn(t.day, t.text, t.amount, t.balance + shift) for t in rows]


BANK = Bank()
BANK.reset()


# ----------------------------------------------------------------- HTML
def inr(x):
    """Indian grouping: INR 1,20,000.00"""
    whole, paise = ("%.2f" % abs(x)).split(".")
    if len(whole) > 3:
        head, tail = whole[:-3], whole[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        whole = ",".join(([head] if head else []) + groups + [tail])
    return ("-" if x < 0 else "") + "INR " + whole + "." + paise


def page(title, body, sid=None, warn=False):
    e = html.escape
    nav = ""
    if sid:
        nav = ('<nav><a href="/accounts">Accounts</a><a href="/transfer">Fund transfer</a>'
               '<a href="/payees">Beneficiaries</a><a href="/bills">Pay bills</a>'
               '<a href="/logout">Log out</a></nav>')
    phone = "".join("<li><span>%s</span> %s</li>" % (e(t), e(m)) for t, m in BANK.phone[:6]) or "<li>No messages</li>"
    warn = warn or bool(sid and BANK.sessions[sid].get("warned"))
    warning = ('<div class="warn" id="warn"%s>Your session ends in 60 seconds. '
               '<a href="/stay">Stay logged in</a></div>' % ("" if warn else ' hidden'))
    script = ""
    if sid:
        s = BANK.sessions[sid]
        idle = BANK.now() - s["last"]
        script = ("<script>setTimeout(function(){document.getElementById('warn').hidden=false},%d);"
                  "setTimeout(function(){location.href='/accounts'},%d);</script>"
                  % (max(0, WARN_AFTER_SECONDS - idle) * 1000, max(0, IDLE_LIMIT_SECONDS - idle) * 1000 + 500))
    clock = datetime.fromtimestamp(BANK.now()).strftime("%d %b %Y %H:%M")
    return """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>%s · NetBank</title>
<style>
@font-face{font-family:Plex;src:url(/fonts/IBMPlexSans-Regular.ttf)}
@font-face{font-family:Plex;font-weight:bold;src:url(/fonts/IBMPlexSans-Bold.ttf)}
@font-face{font-family:PlexMono;src:url(/fonts/IBMPlexMono-Regular.ttf)}
:root{--ink:#111;--line:#bbb;--soft:#f2f2f2;--accent:#0b4f8a;--bad:#a40000;--good:#1d6b2a}
body{font-family:Plex,system-ui,sans-serif;margin:0;color:var(--ink);background:#fff}
header{background:var(--accent);color:#fff;padding:12px 24px;display:flex;justify-content:space-between;align-items:center}
header b{font-size:20px} header span{font-size:13px}
nav{background:var(--soft);padding:8px 24px;border-bottom:1px solid var(--line)}
nav a{margin-right:18px;color:var(--accent);text-decoration:none;font-weight:bold}
main{display:flex;gap:24px;padding:20px 24px;flex-wrap:wrap}
section.page{flex:1 1 560px;max-width:820px} aside{flex:0 0 280px}
h1{font-size:22px;margin:0 0 12px} h2{font-size:17px;margin:20px 0 8px}
table{border-collapse:collapse;width:100%%;margin:8px 0 16px;font-size:14px}
th,td{border:1px solid var(--line);padding:6px 8px;text-align:left} th{background:var(--soft)}
td.n{text-align:right;font-family:PlexMono,monospace}
form{background:var(--soft);padding:12px 14px;border:1px solid var(--line);margin:8px 0 16px}
label{display:block;margin:6px 0 2px;font-size:13px;font-weight:bold}
input,select{font:inherit;padding:5px;width:260px;max-width:100%%}
button{font:inherit;padding:6px 14px;margin-top:10px;background:var(--accent);color:#fff;border:0;cursor:pointer}
.msg{padding:8px 12px;margin:8px 0;border-left:4px solid var(--good);background:#eef6ef}
.err{padding:8px 12px;margin:8px 0;border-left:4px solid var(--bad);background:#fbeeee;color:var(--bad)}
.warn{padding:10px 14px;margin:0 24px;background:#fff3c4;border:1px solid #c9a400}
.box{border:1px solid var(--line);padding:10px 12px;margin-bottom:14px;font-size:13px}
.box ul{list-style:none;padding:0;margin:0} .box li{padding:4px 0;border-bottom:1px dotted var(--line)}
.box li span{color:#555;font-family:PlexMono,monospace;font-size:12px;display:block}
.box form{background:none;border:0;padding:0;margin:4px 0} .box button{margin:2px 4px 2px 0;padding:4px 8px;font-size:12px}
.hint{font-size:13px;color:#444}
</style></head><body>
<header><b>NetBank</b><span>Demo for the NETBANK-DEMO labs · not a real bank</span></header>
%s%s<main><section class="page"><h1>%s</h1>%s</section>
<aside><div class="box"><b>Demo phone (SMS)</b><ul>%s</ul></div>
<div class="box"><b>Demo clock</b><br>%s<br>
<form method="post" action="/clock"><button name="add" value="60">+1 min</button>
<button name="add" value="240">+4 min</button><button name="add" value="86400">+24 h</button></form>
<form method="post" action="/reset"><button>Reset demo data</button></form></div></aside></main>%s</body></html>""" % (
        e(title), nav, warning, e(title), body, phone, clock, script)


def msg(text, ok=True):
    return '<div class="%s">%s</div>' % ("msg" if ok else "err", html.escape(text))


# ----------------------------------------------------------------- pages
class App(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.command, self.path))

    # -- plumbing
    def send(self, text, code=200, headers=()):
        data = text.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        for k, v in headers:
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def redirect(self, where, cookie=None):
        self.send_response(303)
        self.send_header("Location", where)
        if cookie is not None:
            self.send_header("Set-Cookie", cookie)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def form(self):
        n = int(self.headers.get("Content-Length") or 0)
        return {k: v[0] for k, v in parse_qs(self.rfile.read(n).decode()).items()}

    def sid(self):
        c = SimpleCookie(self.headers.get("Cookie", ""))
        return c["sid"].value if "sid" in c else None

    def session(self, touch=True):
        """The logged-in session, or None. Applies the idle timeout (NB-SR2).
        A page shown right after a demo clock jump does not count as activity."""
        sid = self.sid()
        s = BANK.sessions.get(sid)
        if not s or s["state"] != "IN":
            return None, None
        state = session_state(s["last"], BANK.now())
        if state == "EXPIRED":
            del BANK.sessions[sid]
            return None, "Your session has ended"
        s["warned"] = state == "WARNED" and not touch
        if touch:
            s["last"] = BANK.now()
        return sid, None

    def do_GET(self):
        self.route("GET", urlparse(self.path), {})

    def do_POST(self):
        self.route("POST", urlparse(self.path), self.form())

    # -- routing
    def route(self, method, url, f):
        p = url.path
        if p.startswith("/fonts/"):
            return self.font(p[7:])
        if p == "/clock" and method == "POST":
            BANK.offset += float(f.get("add", "0"))
            ref = urlparse(self.headers.get("Referer") or "/")
            back = {"/login": "/otp", "/logout": "/"}.get(ref.path, ref.path or "/")
            query = "&".join(q for q in [ref.query, "clock=1"] if q and q != "clock=1")
            return self.redirect(back + "?" + (query + "&clock=1" if query else "clock=1"))
        if p == "/reset" and method == "POST":
            BANK.reset()
            return self.redirect("/", "sid=; Max-Age=0; Path=/")
        if p == "/" and method == "GET":
            return self.login_page()
        if p == "/login" and method == "POST":
            return self.login(f)
        if p == "/otp" and method == "POST":
            return self.otp(f)
        if p == "/otp":
            s = BANK.sessions.get(self.sid())
            if s and s["state"] == "OTP":
                return self.otp_page(self.sid())
            return self.redirect("/accounts" if s else "/")
        if p == "/logout":
            BANK.sessions.pop(self.sid(), None)
            return self.send(page("Logged out", msg("You have logged out.") + '<a href="/">Log in again</a>'),
                             headers=[("Set-Cookie", "sid=; Max-Age=0; Path=/")])
        sid, ended = self.session(touch="clock=1" not in url.query)
        if not sid:
            return self.login_page(ended or "Please log in first", ok=False)
        handlers = {"/accounts": self.accounts, "/account": self.account_page, "/stay": self.stay,
                    "/statement": self.statement_page, "/transfer": self.transfer,
                    "/confirm": self.confirm, "/payees": self.payees_page, "/bills": self.bills_page}
        h = handlers.get(p)
        if not h:
            return self.send(page("Not found", msg("No such page.", False), sid), 404)
        return h(sid, method, {**{k: v[0] for k, v in parse_qs(url.query).items()}, **f})

    def font(self, name):
        path = os.path.join(HERE, "docs", "fonts", os.path.basename(name))
        if not os.path.exists(path):
            return self.send("", 404)
        data = open(path, "rb").read()
        self.send_response(200)
        self.send_header("Content-Type", "font/ttf")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # -- EP1 login (US1 to US4)
    def login_page(self, note=None, ok=True):
        body = (msg(note, ok) if note else "") + """
<form method="post" action="/login">
<label>Customer ID</label><input name="cid" autocomplete="off">
<label>Password</label><input name="password" type="password">
<br><button>Log in</button></form>
<p class="hint">Demo customer: ID <b>10023456</b>, password <b>Secret#2026</b>.</p>"""
        self.send(page("Log in to NetBank", body))

    def login(self, f):
        cid = f.get("cid", "").strip()
        try:
            BANK.auth.login(cid, f.get("password", ""), BANK.now())
        except LoginError as e:
            BANK.drain_sms()
            c = BANK.auth.customers.get(cid)
            text = str(e)
            if c and "Invalid" in text:
                text += " (failed attempts: %d of 3)" % c.failed_count
            return self.login_page(text, ok=False)
        otp = "%06d" % secrets.randbelow(10 ** 6)
        BANK.auth.send_otp(cid, otp, BANK.now())
        BANK.drain_sms()
        sid = secrets.token_hex(16)
        BANK.sessions[sid] = {"cid": cid, "last": BANK.now(), "otp_tries": 0, "state": "OTP"}
        self.otp_page(sid, cookie="sid=%s; Path=/; HttpOnly" % sid)

    def otp_page(self, sid, note=None, cookie=None):
        body = (msg(note, False) if note else "") + """
<p>We sent a 6-digit OTP to your registered mobile number +91 98450 XXXXX. Read it in the demo phone on the right.</p>
<form method="post" action="/otp"><label>OTP</label><input name="otp" autocomplete="off" maxlength="6">
<br><button>Confirm</button></form>"""
        headers = [("Set-Cookie", cookie)] if cookie else []
        self.send(page("Enter your OTP", body), headers=headers)

    def otp(self, f):
        sid = self.sid()
        s = BANK.sessions.get(sid)
        if not s or s["state"] != "OTP":
            return self.login_page("Please log in first", ok=False)
        try:
            BANK.auth.verify_otp(s["cid"], f.get("otp", "").strip(), BANK.now())
        except LoginError as e:
            text = str(e)
            if text == "OTP expired":
                del BANK.sessions[sid]
                return self.login_page("OTP expired. Log in again to get a new OTP (Resend).", ok=False)
            s["otp_tries"] += 1
            if s["otp_tries"] >= 3:                # LLD-US2: 3 wrong OTPs end the pre-session
                del BANK.sessions[sid]
                return self.login_page("3 wrong OTPs. Log in again.", ok=False)
            return self.otp_page(sid, "%s (attempt %d of 3)" % (text, s["otp_tries"]))
        s["state"], s["last"] = "IN", BANK.now()
        self.redirect("/accounts")

    def stay(self, sid, method, f):
        self.redirect("/accounts")

    # -- EP2 accounts (US5 to US8)
    def accounts(self, sid, method, f):
        by_mask = {a.masked_number: a for a in BANK.accounts}
        rows = "".join('<tr><td>%s</td><td><a href="/account?n=%s">%s</a></td><td class="n">%s</td></tr>'
                       % (k, by_mask[m].number, m, inr(b)) for k, m, b in overview(BANK.accounts))
        body = ("<p>Welcome, %s.</p><table><tr><th>Type</th><th>Account</th><th>Balance</th></tr>%s</table>"
                % (html.escape(NAME), rows))
        self.send(page("Your accounts", body, sid))

    def account_page(self, sid, method, f):
        a = BANK.account(f.get("n", ""))
        rows = [("Account", a.masked_number), ("Type", a.kind), ("Balance", inr(a.balance))]
        if isinstance(a, Savings):
            d = a.details()
            rows += [("Interest rate", "%.2f %% p.a." % d["interest_rate"]), ("Nominee", d["nominee"]),
                     ("IFSC", d["ifsc"]), ("Branch", d["branch"])]
        elif isinstance(a, Current):
            rows += [("Overdraft limit", inr(a.od_limit)), ("Overdraft used", inr(a.od_used)),
                     ("Available", inr(a.available()))]
        else:
            rows += [("EMI", inr(a.emi)), ("Outstanding", inr(-a.balance)),
                     ("Next due date", a.next_due(BANK.today()).strftime("%d %b %Y")),
                     ("Remaining EMIs", str(a.remaining_emis()))]
        body = "<table>%s</table>" % "".join("<tr><th>%s</th><td>%s</td></tr>" % (k, html.escape(v)) for k, v in rows)
        if not isinstance(a, PersonalLoan):
            body += '<p><a href="/statement?n=%s">Statements</a></p>' % a.number
        self.send(page("%s %s" % (a.kind, a.masked_number), body, sid))

    # -- EP3 statements (US9 to US11)
    def statement_page(self, sid, method, f):
        a = BANK.account(f.get("n", ""))
        txns = BANK.txns[a.number]
        body = "<h2>Mini statement</h2>" + txn_table(mini_statement(txns))
        body += ('<h2>Statement for a date range</h2><form method="get" action="/statement">'
                 '<input type="hidden" name="n" value="%s"><label>From</label><input type="date" name="start" value="%s">'
                 '<label>To</label><input type="date" name="end" value="%s"><br><button>Show</button></form>'
                 % (a.number, f.get("start", ""), f.get("end", "")))
        if f.get("start") and f.get("end"):
            try:
                rows = statement(txns, date.fromisoformat(f["start"]), date.fromisoformat(f["end"]), BANK.today())
                body += "<p>%d transactions.</p>%s" % (len(rows), txn_table(rows))
                body += ('<form method="get" action="/statement"><input type="hidden" name="n" value="%s">'
                         '<input type="hidden" name="start" value="%s"><input type="hidden" name="end" value="%s">'
                         '<input type="hidden" name="pdf" value="1"><button>Download PDF</button></form>'
                         % (a.number, f["start"], f["end"]))
                if f.get("pdf"):
                    body += msg("PDF statement ready. It opens only with the password %s "
                                "(first 4 letters of the name and DDMM of the birth date). "
                                "This demo does not create the file." % pdf_password(NAME, BIRTH))
            except ValueError as e:
                body += msg(str(e), False)
        self.send(page("Statements %s" % a.masked_number, body, sid))

    # -- EP4 transfers (US13 to US16)
    def transfer(self, sid, method, f):
        note = ""
        if method == "POST":
            note = self.do_transfer(sid, f)
            if note is None:
                return
        own = "".join('<option value="%s">%s %s, %s</option>' % (a.number, a.kind, a.masked_number, inr(a.balance))
                      for a in (BANK.savings, BANK.current))
        payees = "".join('<option value="p%d">%s, %s</option>' % (i, html.escape(p.name), p.account[-4:])
                         for i, p in enumerate(BANK.payees) if not p.deleted)
        body = note + """
<form method="post" action="/transfer">
<label>From</label><select name="src">%s</select>
<label>Mode</label><select name="mode"><option>Own account</option><option>IMPS</option><option>NEFT</option><option>RTGS</option></select>
<label>To</label><select name="dst">%s<optgroup label="Beneficiaries">%s</optgroup></select>
<label>Amount (INR)</label><input name="amount" inputmode="decimal">
<br><button>Continue</button></form>
<p class="hint">Sent to beneficiaries today: %s. Daily limit INR 10,00,000. IMPS up to INR 5,00,000; RTGS from INR 2,00,000.</p>""" % (
            own, own, payees, inr(BANK.sent_today.get(BANK.today(), 0)))
        self.send(page("Fund transfer", body, sid))

    def do_transfer(self, sid, f):
        try:
            amount = float(f.get("amount", "0").replace(",", ""))
        except ValueError:
            return msg("Enter an amount in rupees, for example 20000", False)
        src = BANK.account(f["src"])
        if f["mode"] == "Own account":
            if f["dst"].startswith("p"):
                return msg("Choose one of your own accounts for an own-account transfer", False)
            dst = BANK.account(f["dst"])
            if dst is src:
                return msg("Choose two different accounts", False)
            try:
                own_transfer(src, dst, amount)           # moves the balances
            except TransferError as e:
                return msg(str(e), False)
            BANK.book(src, "TRANSFER TO %s" % dst.masked_number, -amount)
            BANK.book(dst, "TRANSFER FROM %s" % src.masked_number, amount)
            return msg("Done. Reference %s. Both balances changed." % datetime.fromtimestamp(BANK.now()).strftime("%H%M%S"))
        if not f["dst"].startswith("p"):
            return msg("%s goes to a beneficiary. Choose one under Beneficiaries." % f["mode"], False)
        try:
            check_rules(f["mode"], BANK.payees[int(f["dst"][1:])], src, amount)
        except TransferError as e:
            return msg(str(e), False)
        otp = "%06d" % secrets.randbelow(10 ** 6)
        BANK.sms("OTP %s to send %s by %s." % (otp, inr(amount), f["mode"]))
        text = "Send %s by %s to %s." % (inr(amount), f["mode"], BANK.payees[int(f["dst"][1:])].name)
        BANK.pending[sid] = {"kind": "transfer", "otp": otp, "mode": f["mode"], "src": src.number,
                             "payee": int(f["dst"][1:]), "amount": amount, "text": text}
        self.send(page("Confirm with OTP", confirm_form(text), sid))
        return None

    def confirm(self, sid, method, f):
        if method == "GET":
            p = BANK.pending.get(sid)
            if not p:
                return self.redirect("/accounts")
            return self.send(page("Confirm with OTP", confirm_form(p["text"]), sid))
        p = BANK.pending.pop(sid, None)
        if not p:
            return self.redirect("/accounts")
        otp_ok = f.get("otp", "").strip() == p["otp"]
        if p["kind"] == "payee":
            try:
                add_payee(BANK.payees, p["name"], p["account"], p["account"], p["ifsc"], otp_ok, BANK.now())
                note = msg("Beneficiary added. For the first 24 hours you can send at most INR 50,000 in total to it.")
            except PayeeError as e:
                note = msg(str(e), False)
            return self.payees_page(sid, "GET", {}, note)
        payee = BANK.payees[p["payee"]]
        src = BANK.account(p["src"])
        today = BANK.today()
        try:
            check_rules(p["mode"], payee, src, p["amount"])
            r = third_party_transfer(p["mode"], payee, p["amount"], BANK.sent_today.get(today, 0),
                                     otp_ok, BANK.now())
        except TransferError as e:
            return self.send(page("Fund transfer", msg(str(e), False) + '<a href="/transfer">Back</a>', sid))
        if r["status"] != "SUCCESS":
            return self.send(page("Fund transfer", msg("Transfer failed: " + r["reason"], False), sid))
        BANK.sent_today[today] = BANK.sent_today.get(today, 0) + p["amount"]
        BANK.post(src, "%s/%s/%s" % (p["mode"], r["reference"], payee.name.upper()), -p["amount"])
        self.send(page("Fund transfer", msg("Status: Success. %s reference %s." % (p["mode"], r["reference"]))
                       + '<a href="/transfer">New transfer</a>', sid))

    # -- EP5 beneficiaries (US17, US18)
    def payees_page(self, sid, method, f, note=""):
        if method == "POST" and f.get("delete"):
            try:
                delete_payee(BANK.payees, BANK.payees[int(f["delete"])])
                note = msg("Beneficiary deleted.")
            except PayeeError as e:
                note = msg(str(e), False)
        elif method == "POST":
            if f.get("account") != f.get("account2"):
                note = msg("Account numbers do not match", False)
            elif f.get("ifsc", "").upper() not in KNOWN_IFSC:
                note = msg("Unknown IFSC code", False)
            else:
                otp = "%06d" % secrets.randbelow(10 ** 6)
                BANK.sms("OTP %s to add beneficiary %s." % (otp, f["name"]))
                text = "Add %s, account ending %s, IFSC %s." % (f["name"], f["account"][-4:], f["ifsc"].upper())
                BANK.pending[sid] = {"kind": "payee", "otp": otp, "name": f["name"], "text": text,
                                     "account": f["account"], "ifsc": f["ifsc"].upper()}
                return self.send(page("Confirm with OTP", confirm_form(text), sid))
        rows = "".join(
            '<tr><td>%s</td><td>XXXX%s</td><td>%s</td><td>%s</td><td><form method="post" action="/payees" '
            'style="margin:0;padding:0;border:0;background:none"><button name="delete" value="%d" '
            'style="margin:0">Delete</button></form></td></tr>'
            % (html.escape(p.name), html.escape(p.account[-4:]), p.ifsc,
               "Cooling period" if BANK.now() - p.added_at < 24 * 3600 else "Active", i)
            for i, p in enumerate(BANK.payees) if not p.deleted)
        body = note + ("<table><tr><th>Name</th><th>Account</th><th>IFSC</th><th>Status</th><th></th></tr>%s</table>"
                       % rows if visible(BANK.payees) else "<p>No beneficiaries yet.</p>")
        body += """<h2>Add a beneficiary</h2><form method="post" action="/payees">
<label>Name</label><input name="name" value="Arun Kumar">
<label>Account number</label><input name="account" value="33120045678">
<label>Account number again</label><input name="account2">
<label>IFSC</label><input name="ifsc" value="SBIN0001234">
<br><button>Continue</button></form><p class="hint">Known IFSC codes in this demo: %s.</p>""" % ", ".join(KNOWN_IFSC)
        self.send(page("Beneficiaries", body, sid))

    # -- EP6 bills (US19)
    def bills_page(self, sid, method, f):
        note = ""
        if method == "POST":
            no = f.get("consumer", "").strip()
            if no not in BANK.bills:
                note = msg("No bill found for consumer number %s" % no, False)
            else:
                amount = BANK.bills[no]
                try:
                    receipt = pay_bill(BANK.savings, no, BANK.bills)
                    BANK.book(BANK.savings, "BBPS/ELECTRICITY/" + no, -amount)
                    note = msg("Paid %s. %s" % (inr(amount), receipt))
                except PayeeError as e:
                    note = msg(str(e), False)
        body = note + """<form method="post" action="/bills"><label>Electricity consumer number</label>
<input name="consumer" value="123456789"><br><button>Fetch and pay from Savings</button></form>
<p class="hint">Open bills in this demo: %s.</p>""" % (
            ", ".join("%s (%s)" % (k, inr(v)) for k, v in BANK.bills.items()) or "none")
        self.send(page("Pay bills", body, sid))


def check_rules(mode, payee, src, amount):
    """Limits first (NB-SR8 to NB-SR11), then the balance. Raises TransferError."""
    if amount <= 0:
        raise TransferError("Enter an amount above zero")
    third_party_transfer(mode, payee, amount, BANK.sent_today.get(BANK.today(), 0),
                         otp_ok=False, now=BANK.now())    # raises on a broken limit, changes nothing
    if src.balance < amount:
        raise TransferError("Insufficient balance")


def txn_table(rows):
    if not rows:
        return "<p>No transactions.</p>"
    body = "".join('<tr><td>%s</td><td>%s</td><td class="n">%s</td><td class="n">%s</td></tr>'
                   % (t.day.strftime("%d %b %Y"), html.escape(t.text), inr(t.amount), inr(t.balance))
                   for t in rows)
    return ("<p>%d rows</p><table><tr><th>Date</th><th>Description</th><th>Amount</th><th>Balance</th></tr>%s</table>"
            % (len(rows), body))


def confirm_form(text):
    return ("<p>%s</p><p>We sent an OTP to your registered mobile number. Read it in the demo phone.</p>"
            '<form method="post" action="/confirm"><label>OTP</label><input name="otp" maxlength="6" autocomplete="off">'
            "<br><button>Confirm</button></form>" % html.escape(text))


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    host = os.environ.get("NETBANK_HOST", "127.0.0.1")
    print("NetBank demo on http://localhost:%d  (customer 10023456, password Secret#2026)" % port)
    print("Press Ctrl+C to stop.")
    HTTPServer((host, port), App).serve_forever()
