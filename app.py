"""Vtab Office Suite 365 V7 — PostgreSQL (Supabase) edition."""

from __future__ import annotations

import os as _os

import base64
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import hmac
import html
import json
import os
from pathlib import Path
import sqlite3
import secrets
from typing import Any
import urllib.parse


BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = None
DB_PATH = os.environ.get("VTAB_DB_PATH", BASE_DIR / "vtab_office_suite.db")
HOST = os.environ.get("VTAB_HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", os.environ.get("VTAB_PORT", "8000")))
SECRET_KEY = os.environ.get("VTAB_SECRET_KEY", "vtab-local-development-key-change-me").encode()
COOKIE_NAME = "vtab_session"


def esc(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


# ---------------------------------------------------------------------------
# Database abstraction
# Wraps psycopg2 so every call site (with db() as con: con.execute(...))
# is identical to the original sqlite3 usage.
# ---------------------------------------------------------------------------

import psycopg2
from psycopg2.extras import RealDictCursor

@contextmanager
def db():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL must be set")
    conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    try:
        # We return conn directly since psycopg2 cursor behaves similarly
        # but we need to patch execute and executemany on the connection
        # to match sqlite3 interface where conn.execute returns a cursor
        class _PgCon:
            def __init__(self, c):
                self._c = c
            def execute(self, sql, params=()):
                cur = self._c.cursor()
                cur.execute(sql.replace("?", "%s"), params)
                return cur
            def executemany(self, sql, seq):
                cur = self._c.cursor()
                cur.executemany(sql.replace("?", "%s"), list(seq))
                return cur
        yield _PgCon(conn)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Password helpers (unchanged — PBKDF2 logic is DB-independent)
# ---------------------------------------------------------------------------

def password_hash(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 240_000)
    return f"pbkdf2_sha256${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"


def password_ok(password: str, stored: str) -> bool:
    try:
        _, salt_text, digest_text = stored.split("$", 2)
        salt = base64.urlsafe_b64decode(salt_text)
        actual = password_hash(password, salt).split("$", 2)[2]
        return hmac.compare_digest(actual, digest_text)
    except (ValueError, TypeError):
        return False


# ---------------------------------------------------------------------------
# Database initialisation (PostgreSQL schema — SERIAL, no AUTOINCREMENT/PRAGMA)
# CREATE TABLE IF NOT EXISTS is a no-op when tables already exist in Supabase.
# ---------------------------------------------------------------------------

def init_database() -> None:
    with db() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id            SERIAL  PRIMARY KEY,
                name          TEXT    NOT NULL,
                email         TEXT    NOT NULL UNIQUE,
                password_hash TEXT    NOT NULL,
                role          TEXT    NOT NULL,
                department    TEXT    NOT NULL,
                employee_id   TEXT    NOT NULL UNIQUE,
                registered_at TEXT    NOT NULL,
                active        INTEGER NOT NULL DEFAULT 1
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS applications(
                id            SERIAL  PRIMARY KEY,
                slug          TEXT    NOT NULL UNIQUE,
                name          TEXT    NOT NULL,
                description   TEXT    NOT NULL,
                category      TEXT    NOT NULL,
                icon          TEXT    NOT NULL,
                color         TEXT    NOT NULL,
                url           TEXT    NOT NULL,
                sso_mode      TEXT    NOT NULL,
                enabled       INTEGER NOT NULL DEFAULT 1,
                built_in      INTEGER NOT NULL DEFAULT 0,
                allowed_roles TEXT    NOT NULL,
                version       TEXT    NOT NULL,
                publisher     TEXT    NOT NULL,
                created_at    TEXT    NOT NULL,
                visibility    TEXT    NOT NULL DEFAULT 'everyone',
                logo_url      TEXT    NOT NULL DEFAULT ''
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS sessions(
                id          TEXT    PRIMARY KEY,
                user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                csrf_token  TEXT    NOT NULL,
                created_at  TEXT    NOT NULL,
                expires_at  TEXT    NOT NULL
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs(
                id          SERIAL PRIMARY KEY,
                created_at  TEXT   NOT NULL,
                event_type  TEXT   NOT NULL,
                user_email  TEXT   NOT NULL,
                app_name    TEXT,
                details     TEXT   NOT NULL,
                status      TEXT   NOT NULL
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS announcements(
                id               SERIAL  PRIMARY KEY,
                title            TEXT    NOT NULL,
                app_name         TEXT    NOT NULL,
                version          TEXT    NOT NULL,
                description      TEXT    NOT NULL,
                status           TEXT    NOT NULL,
                created_at       TEXT    NOT NULL,
                release_date     TEXT    NOT NULL DEFAULT '',
                highlights       TEXT    NOT NULL DEFAULT '',
                progress_percent INTEGER NOT NULL DEFAULT 0
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS notifications(
                id         SERIAL  PRIMARY KEY,
                user_id    INTEGER REFERENCES users(id) ON DELETE CASCADE,
                title      TEXT    NOT NULL,
                message    TEXT    NOT NULL,
                category   TEXT    NOT NULL,
                is_read    INTEGER NOT NULL DEFAULT 0,
                created_at TEXT    NOT NULL
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS leave_requests(
                id         SERIAL  PRIMARY KEY,
                user_id    INTEGER NOT NULL REFERENCES users(id),
                leave_type TEXT    NOT NULL,
                start_date TEXT    NOT NULL,
                end_date   TEXT    NOT NULL,
                reason     TEXT    NOT NULL,
                status     TEXT    NOT NULL DEFAULT 'Pending',
                created_at TEXT    NOT NULL
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS appraisals(
                id         SERIAL  PRIMARY KEY,
                user_id    INTEGER NOT NULL REFERENCES users(id),
                quarter    TEXT    NOT NULL,
                feedback   TEXT    NOT NULL,
                created_at TEXT    NOT NULL
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS payroll_records(
                id           SERIAL  PRIMARY KEY,
                user_id      INTEGER NOT NULL REFERENCES users(id),
                month        TEXT    NOT NULL,
                base_salary  NUMERIC NOT NULL,
                housing      NUMERIC NOT NULL,
                bonus        NUMERIC NOT NULL,
                tax          NUMERIC NOT NULL,
                insurance    NUMERIC NOT NULL,
                bank_account TEXT    NOT NULL,
                payment_date TEXT    NOT NULL
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS user_quick_access(
                user_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                app_id   INTEGER NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
                position INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (user_id, app_id)
            )
        """)
        if not con.execute("SELECT 1 FROM users LIMIT 1").fetchone():
            con.executemany("INSERT INTO users(name,email,password_hash,role,department,employee_id,registered_at) VALUES(%s,%s,%s,%s,%s,%s,%s)", [
                ("Elena Rostova", "admin@vtaboffice365.com", password_hash("Admin@123"), "Administrator", "IT & Security Operations", "ADM-001", "2024-11-10"),
                ("Sarah Jenkins", "user@vtaboffice365.com", password_hash("User@123"), "Employee", "Operations", "EMP-204", "2025-01-15"),
            ])
        if not con.execute("SELECT 1 FROM applications LIMIT 1").fetchone():
            apps = [
                ("appraisal","Appraisal & Performance","Quarterly OKRs, self-appraisals, peer feedback and career growth plans.","performance","AP","#4f46e5","/app/appraisal","oidc",1,1,'["All Employees"]',"v2.8.4","Vtab Talent","everyone"),
                ("hr-portal","HR Portal & Directory","Employee directory, onboarding, leave workflows and document management.","hr","HR","#059669","/app/hr-portal","oidc",1,1,'["All Employees"]',"v3.2.0","Vtab People Operations","everyone"),
                ("payroll","Payroll & Compensation","Salary statements, benefits, tax deductions and secure payslip downloads.","finance","PY","#2563eb","/app/payroll","saml2",1,1,'["All Employees"]',"v4.1.1","Vtab Finance","everyone"),
                ("attendance","Attendance & Leave Suite","Time tracking, shift planning, leave management and holiday calendars.","hr","AT","#0d9488","https://attendance.example.internal","jwt_header",1,0,'["All Employees"]',"v1.9.0","Vtab Operations","everyone"),
                ("expenses","Expense Claims Portal","Travel receipts, reimbursement requests and department budget tracking.","finance","EX","#d97706","https://expenses.example.internal","oidc",1,0,'["All Employees"]',"v2.1.0","Vtab Finance","everyone"),
                ("desk-booking","Smart Office & Desk Booking","Workspace reservations, meeting rooms and interactive floor plans.","operations","DB","#9333ea","https://desk.example.internal","shared_session",1,0,'["All Employees"]',"v1.4.2","Vtab Workplace","everyone"),
                ("meet-assistant","Meet Assistant","Meeting agendas, notes, action items and searchable summaries.","productivity","MA","#db2777","/app/meet-assistant","oidc",1,0,'["All Employees"]',"v1.0.0","Vtab Collaboration","everyone"),
                ("workspace-control","Workspace Control Center","Administrator tools for application governance, access policies and workspace configuration.","operations","WC","#6d4bc3","/admin","oidc",1,1,'["Administrator"]',"v1.0.0","Vtab IT","admins"),
            ]
            con.executemany("INSERT INTO applications(slug,name,description,category,icon,color,url,sso_mode,enabled,built_in,allowed_roles,version,publisher,created_at,visibility) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", [a[:-1] + (now_iso(), a[-1]) for a in apps])
        if not con.execute("SELECT 1 FROM announcements LIMIT 1").fetchone():
            con.executemany("INSERT INTO announcements(title,app_name,version,description,status,created_at,release_date,highlights,progress_percent) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)", [
                ("Meeting Intelligence","Vtab Meet Intelligence","v1.0 Preview","Turn conversations into searchable decisions, summaries and assigned follow-up actions.","Planned",now_iso(),"Q1 2027","Decision tracking|Automatic action items|Searchable meeting memory",35),
                ("Smarter workspace reservations","Asset & Desk Planner","v1.0","Reserve desks, meeting rooms and shared equipment from one visual workspace map.","Beta Testing",now_iso(),"Q4 2026","Interactive floor maps|Equipment reservations|Team neighbourhoods",62),
                ("AI Copilot Workspace","Vtab AI Copilot","v1.0 Beta","Cross-application summaries, scheduling and document drafting.","Coming Soon",now_iso(),"Q4 2026","Cross-app summaries|Smart scheduling|Document drafting",75),
                ("Unified Workspace is live","Vtab Office Suite 365","v1.0.0","One account now opens every registered workplace application.","Live Now",now_iso(),"Available now","Unified sign-in|Application launcher|Secure sessions",100),
            ])
        for user in con.execute("SELECT id FROM users").fetchall():
            if not con.execute("SELECT 1 FROM payroll_records WHERE user_id=%s", (user["id"],)).fetchone():
                con.execute("INSERT INTO payroll_records(user_id,month,base_salary,housing,bonus,tax,insurance,bank_account,payment_date) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)", (user["id"],"August 2026",5800,1200,750,820,180,"Vtab Bank \u2022\u2022\u2022\u2022 4821","2026-08-28"))


def nav_icon(name: str) -> str:
    paths = {
        "home":"<path d='M3 11l9-8 9 8v9a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1z'/>",
        "apps":"<rect x='3' y='3' width='7' height='7' rx='1'/><rect x='14' y='3' width='7' height='7' rx='1'/><rect x='3' y='14' width='7' height='7' rx='1'/><rect x='14' y='14' width='7' height='7' rx='1'/>",
        "news":"<rect x='4' y='4' width='16' height='16' rx='2'/><path d='M8 8h8M8 12h8M8 16h5'/>",
        "shield":"<path d='M12 3l8 3v6c0 5-3.4 8.1-8 9-4.6-.9-8-4-8-9V6z'/><path d='M9 12l2 2 4-4'/>",
        "admin":"<path d='M4 21V8l8-5 8 5v13M8 21v-6h8v6'/>",
        "settings":"<circle cx='12' cy='12' r='3'/><path d='M19 12l2-1-2-4-2 1-2-2V3h-6v3L7 8 5 7l-2 4 2 1v2l-2 1 2 4 2-1 2 2v1h6v-1l2-2 2 1 2-4-2-1z'/>",
        "search":"<circle cx='11' cy='11' r='7'/><path d='M16 16l5 5'/>",
        "plus":"<path d='M12 5v14M5 12h14'/>",
        "logout":"<path d='M10 5H5v14h5M14 8l4 4-4 4M18 12H9'/>",
    }
    return f'<svg class="nav-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths.get(name, paths["apps"])}</svg>'


# Inline SVG icon library — no CDN required, always renders
_SVG_ICONS = {
    "fa-chart-line":        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
    "fa-sliders":           '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/></svg>',
    "fa-file-invoice-dollar": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="11" x2="12" y2="17"/><line x1="9" y1="13" x2="15" y2="13"/></svg>',
    "fa-users":             '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "fa-window-maximize":   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="18" rx="2"/><line x1="2" y1="8" x2="22" y2="8"/></svg>',
    "fa-user-shield":       '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/></svg>',
    "fa-file-signature":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 19.5v.5a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8.5L18 5.5"/><path d="M8 18h1l12.5-12.5-1-1L8 17v1z"/></svg>',
    "fa-database":          '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
    "fa-bolt":              '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    "fa-exchange-alt":      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg>',
    "fa-vial":              '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2v17.5c0 1.4-1.1 2.5-2.5 2.5h0c-1.4 0-2.5-1.1-2.5-2.5V2"/><path d="M8.5 2h7"/><path d="M14.5 16h-5"/></svg>',
    "fa-building":          '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="1"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01M16 6h.01M12 6h.01M8 10h.01M16 10h.01M12 10h.01M8 14h.01M16 14h.01M12 14h.01"/></svg>',
}

def _get_svg(icon_val: str) -> str | None:
    """Extract the last fa-xxx keyword from an icon class string and look it up."""
    import re as _re
    keys = _re.findall(r'fa-[\w-]+', icon_val)
    for key in reversed(keys):
        if key in _SVG_ICONS:
            return _SVG_ICONS[key]
    return None

def product_icon(app: dict, small: bool = False) -> str:
    size = " product-icon-small" if small else ""
    logo = app.get("logo_url")
    if logo:
        return f'<span class="product-icon{size} custom-logo"><img src="{esc(logo)}" alt=""></span>'

    icon_val = str(app.get("icon", "")).strip()
    svg = _get_svg(icon_val)
    if svg:
        content = svg
    else:
        import re
        clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', app.get("name", ""))
        words = [w for w in clean_name.split() if w.strip()]
        if not words:
            initials = "VT"
        elif len(words) == 1:
            initials = words[0][:2].upper()
        else:
            initials = (words[0][0] + words[1][0]).upper()
        content = f'<b>{esc(initials)}</b>'

    return f'<span class="product-icon{size}" style="--app-color:{esc(app["color"])}">{content}</span>'


def application_card(app: dict, admin: bool = False) -> str:
    label = "Admin only" if admin or app["visibility"] == "admins" else "Workspace"
    return f'<a class="card app-card" data-category="{esc(app["category"])}" data-search="{esc((app["name"]+" "+app["description"]).lower())}" href="/app/{esc(app["slug"])}" style="--app-tint:{esc(app["color"])}18"><div class="app-top">{product_icon(app)}<span class="visibility-pill {"admins" if label == "Admin only" else ""}">{label}</span></div><h3>{esc(app["name"])}</h3><p>{esc(app["description"])}</p><div class="meta"><span>{esc(app["category"].title())}</span><span>{esc(app["version"])}</span></div></a>'


def send_email_otp(to_email: str, otp_code: str):
    import urllib.request
    import json
    import os
    url = "https://api.brevo.com/v3/smtp/email"
    brevo_api_key = os.getenv("BREVO_API_KEY")
    if not brevo_api_key:
        print("Warning: BREVO_API_KEY environment variable not set. Email will not be sent.")
        return
        
    sender_email = os.getenv("AUTH_EMAIL_FROM", "vitabsquare@gmail.com")
    sender_name = os.getenv("AUTH_EMAIL_NAME", "VTAB365")
    
    headers = {
        "accept": "application/json",
        "api-key": brevo_api_key,
        "content-type": "application/json"
    }
    data = {
        "sender": {"name": sender_name, "email": sender_email},
        "to": [{"email": to_email}],
        "subject": "Your VTAB 365 Login Code",
        "htmlContent": f"<html><body><h2>Your sign in code</h2><p>Here is your 6-digit verification code to sign into VTAB 365:</p><h1 style='letter-spacing:5px;'>{otp_code}</h1><p>This code will expire in 5 minutes.</p></body></html>"
    }
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers)
        with urllib.request.urlopen(req) as res:
            pass
    except Exception as e:
        print(f"Failed to send OTP email: {e}")

class VtabHandler(BaseHTTPRequestHandler):
    server_version = "VtabOffice/7.0"

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[{self.log_date_time_string()}] {fmt % args}")

    def send_bytes(self, body: bytes, status: int = 200, content_type: str = "text/html; charset=utf-8", headers: dict[str, str] | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; img-src 'self' data: https:; form-action 'self'; frame-ancestors 'self'")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def text(self, value: str, status: int = 200, content_type: str = "text/html; charset=utf-8", headers: dict[str, str] | None = None) -> None:
        self.send_bytes(value.encode("utf-8"), status, content_type, headers)

    def redirect(self, target: str, cookie: str | None = None) -> None:
        headers = {"Location": target}
        if cookie:
            headers["Set-Cookie"] = cookie
        self.send_bytes(b"", 303, headers=headers)

    def route(self) -> tuple[str, dict[str, list[str]]]:
        parsed = urllib.parse.urlparse(self.path)
        return parsed.path.rstrip("/") or "/", urllib.parse.parse_qs(parsed.query)

    def form(self) -> dict[str, str]:
        try:
            length = min(int(self.headers.get("Content-Length", "0")), 1_000_000)
        except ValueError:
            length = 0
        data = urllib.parse.parse_qs(self.rfile.read(length).decode("utf-8", "replace"), keep_blank_values=True)
        return {key: values[-1] for key, values in data.items()}

    def audit(self, event: str, email: str, details: str, app: str | None = None, status: str = "SUCCESS") -> None:
        with db() as con:
            con.execute("INSERT INTO audit_logs(created_at,event_type,user_email,app_name,details,status) VALUES(%s,%s,%s,%s,%s,%s)", (now_iso(),event,email,app,details,status))

    def new_session(self, user_id: int) -> str:
        sid, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(24)
        expiry = datetime.now(timezone.utc) + timedelta(hours=12)
        with db() as con:
            con.execute("INSERT INTO sessions(id,user_id,csrf_token,created_at,expires_at) VALUES(%s,%s,%s,%s,%s)", (sid,user_id,csrf,now_iso(),expiry.isoformat()))
        signature = hmac.new(SECRET_KEY, sid.encode(), hashlib.sha256).hexdigest()
        return f"{COOKIE_NAME}={sid}.{signature}; Path=/; HttpOnly; SameSite=Lax; Max-Age=43200"

    def current_session(self) -> tuple[dict | None, dict | None]:
        jar = cookies.SimpleCookie()
        try:
            jar.load(self.headers.get("Cookie", ""))
            signed = jar.get(COOKIE_NAME).value if jar.get(COOKIE_NAME) else ""
            sid, supplied = signed.split(".", 1)
            expected = hmac.new(SECRET_KEY, sid.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(supplied, expected):
                return None, None
            with db() as con:
                session = con.execute("SELECT * FROM sessions WHERE id=%s AND expires_at>%s", (sid,now_iso())).fetchone()
                user = con.execute("SELECT * FROM users WHERE id=%s AND active=1", (session["user_id"],)).fetchone() if session else None
            return user, session
        except (ValueError, KeyError):
            return None, None

    def require_user(self) -> tuple[dict | None, dict | None]:
        user, session = self.current_session()
        if not user:
            self.redirect("/login")
        return user, session

    def flash(self, target: str, message: str, error: bool = False) -> None:
        join = "&" if "?" in target else "?"
        self.redirect(f"{target}{join}{'error' if error else 'ok'}={urllib.parse.quote(message)}")

    def check_csrf(self, form: dict[str, str], session: dict) -> bool:
        return hmac.compare_digest(form.get("csrf", ""), session["csrf_token"])

    def layout(self, title: str, content: str, user: dict | None = None, session: dict | None = None, active: str = "home", query: dict[str, list[str]] | None = None) -> str:
        flashes = ""
        query = query or {}
        if query.get("ok"):
            flashes += f'<div class="flash">{esc(query["ok"][0])}</div>'
        if query.get("error"):
            flashes += f'<div class="flash error">{esc(query["error"][0])}</div>'
        head = f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} &middot; Vtab 365</title><link rel="icon" type="image/png" href="/favicon.ico"><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/css/all.min.css"><link rel="stylesheet" href="/assets/style.css?v=5"></head><body>'
        if not user:
            return head + content + '<script src="/assets/app.js"></script></body></html>'
        with db() as con:
            pinned = con.execute("SELECT a.* FROM user_quick_access q JOIN applications a ON a.id=q.app_id WHERE q.user_id=%s AND a.enabled=1 AND (a.visibility='everyone' OR %s='Administrator') ORDER BY q.position LIMIT 6", (user["id"],user["role"])).fetchall()
            if not pinned:
                pinned = con.execute("SELECT * FROM applications WHERE enabled=1 AND visibility='everyone' ORDER BY built_in DESC,name LIMIT 3").fetchall()
        admin_nav = ""
        if user["role"] == "Administrator":
            admin_nav = f'<div class="nav-label">Administration</div><a class="{"active" if active=="admin-apps" else ""}" href="/admin-apps">{nav_icon("admin")}<span>Admin applications</span></a><a class="{"active" if active=="admin" else ""}" href="/admin">{nav_icon("settings")}<span>App settings</span></a>'
        side_apps = "".join(f'<a href="/app/{esc(a["slug"])}">{product_icon(a,True)}<span>{esc(a["name"])}</span></a>' for a in pinned)
        initials = "".join(part[0] for part in user["name"].split()[:2]).upper()
        add = f'<a class="btn" href="/admin">{nav_icon("plus")}Add app</a>' if user["role"] == "Administrator" else ""
        return head + f'<div class="shell"><aside class="sidebar"><div class="brand"><img class="brandmark" src="/logo.png" alt="VTAB 365"><div><strong>Vtab 365</strong><small>Office workspace</small></div></div><nav class="nav"><div class="nav-label">Workspace</div><a class="{"active" if active=="home" else ""}" href="/">{nav_icon("home")}<span>Home</span></a><a class="{"active" if active=="apps" else ""}" href="/apps">{nav_icon("apps")}<span>All applications</span></a><a class="{"active" if active=="updates" else ""}" href="/updates">{nav_icon("news")}<span>What\'s new</span></a><a class="{"active" if active=="sso" else ""}" href="/sso">{nav_icon("shield")}<span>Security &amp; SSO</span></a>{admin_nav}<div class="sidebar-section-head"><div class="nav-label">Quick access</div><a class="quick-settings" href="/quick-access">Customize</a></div><div class="sidebar-apps">{side_apps}</div></nav><div class="side-user"><div class="avatar">{esc(initials)}</div><div class="user-copy"><strong>{esc(user["name"])}</strong><small>{esc(user["role"])}</small><small>{esc(user["email"])}</small></div></div></aside><section class="main"><header class="topbar"><div class="top-search">{nav_icon("search")}<input id="app-search" class="search" placeholder="Search applications"></div><div class="actions">{add}<div class="top-avatar">{esc(initials[:1])}</div><form method="post" action="/logout"><input type="hidden" name="csrf" value="{esc(session["csrf_token"])}"><button class="btn secondary icon-btn" title="Sign out" aria-label="Sign out">{nav_icon("logout")}</button></form></div></header><main class="content">{flashes}{content}</main></section></div><script src="/assets/app.js"></script></body></html>'

    def login_page(self, query: dict[str, list[str]]) -> str:
        error = f'<div class="flash error">{esc(query["error"][0])}</div>' if query.get("error") else ""
        content = f'<div class="login-page"><div class="login-card"><img class="brandmark" src="/logo.png" alt="VTAB 365"><h1>Welcome to Vtab 365</h1><p>One secure account for every workplace application.</p>{error}<form method="post" action="/login" class="grid-form"><div class="field full"><label>Work email</label><input type="email" name="email" required></div><div class="field full"><label>Password</label><input type="password" name="password" required></div><div class="field full"><button class="btn">Sign in to workspace</button></div></form><p style="text-align:center"><a href="/register">Create an employee account</a></p></div></div>'
        return self.layout("Sign in", content)

    def verify_otp_page(self, query: dict[str, list[str]]) -> str:
        error = f'<div class="flash error">{esc(query["error"][0])}</div>' if query.get("error") else ""
        content = f'<div class="login-page"><div class="login-card"><img class="brandmark" src="/logo.png" alt="VTAB 365"><h1>Two-Factor Authentication</h1><p>We sent a 6-digit code to your email. Please enter it below to continue.</p>{error}<form method="post" action="/verify-otp" class="grid-form"><div class="field full"><label>Verification Code</label><input type="text" name="otp_code" placeholder="123456" required autocomplete="off"></div><div class="field full"><button class="btn">Verify and Sign in</button></div></form><p style="text-align:center"><a href="/login">Back to sign in</a></p></div></div>'
        return self.layout("Verify OTP", content)

    def dashboard(self, user: dict, session: dict, query: dict[str,list[str]]) -> str:
        with db() as con:
            apps = con.execute("SELECT * FROM applications WHERE enabled=1 AND (visibility='everyone' OR (visibility='admins' AND %s='Administrator')) ORDER BY built_in DESC,name", (user["role"],)).fetchall()
            releases = con.execute("SELECT * FROM announcements ORDER BY CASE WHEN status='Live Now' THEN 1 ELSE 0 END,id DESC LIMIT 6").fetchall()
            pinned = con.execute("SELECT a.* FROM user_quick_access q JOIN applications a ON a.id=q.app_id WHERE q.user_id=%s AND a.enabled=1 AND (a.visibility='everyone' OR %s='Administrator') ORDER BY q.position LIMIT 6", (user["id"],user["role"])).fetchall() or apps[:4]
        categories = sorted({a["category"] for a in apps})
        chips = '<button class="chip active" data-cat="all">All</button>' + "".join(f'<button class="chip" data-cat="{esc(c)}">{esc(c.title())}</button>' for c in categories)
        quick = "".join(f'<a class="quick-access-tile" href="/app/{esc(a["slug"])}">{product_icon(a,True)}<span>{esc(a["name"])}</span></a>' for a in pinned)
        release_html = ""
        for item in releases:
            highlights = "".join(f'<span>{esc(x.strip())}</span>' for x in item["highlights"].split("|")[:3] if x.strip())
            cls = item["status"].lower().replace(" ","-")
            release_html += f'<article class="home-release-card"><div class="home-release-top"><span class="release-status {esc(cls)}">{esc(item["status"])}</span><span class="release-date">{esc(item["release_date"] or item["version"])}</span></div><h3>{esc(item["title"])}</h3><p>{esc(item["description"])}</p><div class="home-release-highlights">{highlights}</div><div class="home-release-footer"><div class="home-release-product"><strong>{esc(item["app_name"])}</strong><small>{esc(item["version"])}</small></div><a class="home-release-link" href="/updates#release-{item["id"]}">View release details →</a></div></article>'
        admin = f'<div class="intro-actions"><a class="btn secondary" href="/admin-apps">Admin applications</a><a class="btn" href="/admin">{nav_icon("plus")}Add application</a></div>' if user["role"] == "Administrator" else ""
        content = f'<section class="page-intro"><div><div class="eyebrow">Vtab Office Suite</div><h1>Your applications</h1><p>Everything you need to work, in one simple and secure workspace.</p></div>{admin}</section><section class="panel quick-access-panel"><div class="quick-access-head"><div><h2>Quick access</h2><p>Your chosen tools, ready to launch with your Vtab account.</p></div><a class="btn secondary" href="/quick-access">Customize</a></div><div class="quick-access-grid">{quick}</div></section><div class="section-head" id="apps"><div><h2>All applications</h2><p>Tools available to everyone in the workspace.</p></div><a class="section-link" href="/apps">Open full launcher →</a></div><div class="filters">{chips}</div><div class="grid">{"".join(application_card(a) for a in apps)}</div><div class="section-head"><div><h2>What\'s new and upcoming</h2><p>Latest workspace releases and applications planned for your team.</p></div><a class="section-link" href="/updates">View all releases →</a></div><div class="home-release-grid">{release_html}</div>'
        return self.layout("Workspace",content,user,session,"home",query)

    def apps_page(self,user,session,query):
        with db() as con: apps=con.execute("SELECT * FROM applications WHERE enabled=1 AND (visibility='everyone' OR (visibility='admins' AND %s='Administrator')) ORDER BY built_in DESC,name", (user["role"],)).fetchall()
        cats=sorted({a["category"] for a in apps}); chips='<button class="chip active" data-cat="all">All</button>'+"".join(f'<button class="chip" data-cat="{esc(c)}">{esc(c.title())}</button>' for c in cats)
        return self.layout("All applications",f'<section class="page-intro"><div><div class="eyebrow">Application launcher</div><h1>All applications</h1><p>Browse every tool available to your workspace account.</p></div><a class="btn secondary page-home" href="/">{nav_icon("home")}Home</a></section><div class="filters">{chips}</div><div class="grid">{"".join(application_card(a) for a in apps)}</div>',user,session,"apps",query)

    def updates_page(self,user,session,query):
        with db() as con: items=con.execute("SELECT * FROM announcements ORDER BY CASE WHEN status='Live Now' THEN 1 ELSE 0 END,id DESC").fetchall()
        timeline=""
        for item in items:
            high="".join(f'<span>{esc(x.strip())}</span>' for x in item["highlights"].split("|") if x.strip()); progress=max(0,min(100,int(item["progress_percent"] or 0)))
            timeline+=f'<article id="release-{item["id"]}" class="timeline-item"><div class="timeline-date">{esc(item["release_date"] or item["status"])}</div><div><span class="badge">{esc(item["status"])}</span><h3>{esc(item["title"])}</h3><p>{esc(item["description"])}</p><div class="highlight-list">{high}</div><div class="progress-line"><span style="width:{progress}%"></span></div><small>{esc(item["app_name"])} · {esc(item["version"])}</small></div></article>'
        return self.layout("What's new",f'<section class="page-intro"><div><div class="eyebrow">Release centre</div><h1>What\'s new and upcoming</h1><p>Follow live improvements and applications planned for your workspace.</p></div><a class="btn secondary page-home" href="/">{nav_icon("home")}Home</a></section><div class="timeline">{timeline}</div>',user,session,"updates",query)

    def quick_page(self,user,session,query):
        with db() as con:
            apps=con.execute("SELECT * FROM applications WHERE enabled=1 AND (visibility='everyone' OR %s='Administrator') ORDER BY visibility,built_in DESC,name",(user["role"],)).fetchall()
            selected={r["app_id"] for r in con.execute("SELECT app_id FROM user_quick_access WHERE user_id=%s",(user["id"],)).fetchall()}
        choices="".join(f'<label class="quick-choice"><input type="checkbox" name="app_{a["id"]}" {"checked" if a["id"] in selected else ""}>{product_icon(a,True)}<span class="quick-choice-copy"><strong>{esc(a["name"])}</strong><small>{esc(a["category"].title())}{" · Admin only" if a["visibility"]=="admins" else ""}</small></span></label>' for a in apps)
        return self.layout("Customize Quick Access",f'<section class="page-intro"><div><div class="eyebrow">Personal workspace</div><h1>Customize Quick Access</h1><p>Choose up to six applications for Home and the sidebar.</p></div><a class="btn secondary page-home" href="/">{nav_icon("home")}Home</a></section><form class="panel" method="post" action="/quick-access/save"><input type="hidden" name="csrf" value="{esc(session["csrf_token"])}"><div class="quick-picker">{choices}</div><button class="btn">Save Quick Access</button></form>',user,session,"quick",query)

    def sso_page(self,user,session,query):
        with db() as con: apps=con.execute("SELECT * FROM applications WHERE enabled=1 AND (visibility='everyone' OR %s='Administrator') ORDER BY name",(user["role"],)).fetchall()
        rows="".join(f'<tr><td><div class="manage-app">{product_icon(a,True)}<strong>{esc(a["name"])}</strong></div></td><td>{esc(a["sso_mode"].upper())}</td><td><span class="status">Connected</span></td></tr>' for a in apps)
        return self.layout("Security & SSO",f'<section class="page-intro"><div><div class="eyebrow">Identity</div><h1>Security &amp; SSO</h1><p>Your Vtab identity securely connects permitted applications.</p></div><a class="btn secondary page-home" href="/">{nav_icon("home")}Home</a></section><div class="panel table-wrap"><table><thead><tr><th>Application</th><th>Protocol</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table></div>',user,session,"sso",query)

    def admin_apps_page(self,user,session,query):
        with db() as con: apps=con.execute("SELECT * FROM applications WHERE enabled=1 AND visibility='admins' ORDER BY name").fetchall()
        return self.layout("Admin applications",f'<section class="panel admin-hero admin-app-banner"><div><div class="eyebrow">Administration</div><h1>Admin applications</h1><p>Protected operational tools available only to administrator accounts.</p></div><div class="intro-actions"><a class="btn secondary page-home" href="/">{nav_icon("home")}Home</a><a class="btn secondary" href="/admin">Manage settings</a></div></section><div class="grid admin-grid">{"".join(application_card(a,True) for a in apps)}</div>',user,session,"admin-apps",query)

    def admin_page(self,user,session,query):
        with db() as con:
            apps=con.execute("SELECT * FROM applications ORDER BY built_in DESC,name").fetchall()
            announcements=con.execute("SELECT * FROM announcements ORDER BY id DESC").fetchall()
            logs=con.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 40").fetchall()
            users_list=con.execute("SELECT * FROM users ORDER BY name").fetchall()
        app_rows=""
        for a in apps:
            opts=f'<option value="everyone" {"selected" if a["visibility"]=="everyone" else ""}>Everyone</option><option value="admins" {"selected" if a["visibility"]=="admins" else ""}>Administrators only</option>'
            remove="" if a["built_in"] else f'<form method="post" action="/admin/apps/delete"><input type="hidden" name="csrf" value="{esc(session["csrf_token"])}"><input type="hidden" name="id" value="{a["id"]}"><button class="btn danger compact-btn">Remove</button></form>'
            app_rows+=f'<tr><td><div class="manage-app">{product_icon(a,True)}<strong>{esc(a["name"])}</strong></div></td><td>{esc(a["category"].title())}</td><td><form class="settings-form" method="post" action="/admin/apps/settings"><input type="hidden" name="csrf" value="{esc(session["csrf_token"])}"><input type="hidden" name="id" value="{a["id"]}"><select name="visibility">{opts}</select><button class="btn secondary compact-btn">Save</button></form></td><td><form method="post" action="/admin/apps/toggle"><input type="hidden" name="csrf" value="{esc(session["csrf_token"])}"><input type="hidden" name="id" value="{a["id"]}"><button class="btn secondary compact-btn">{"Disable" if a["enabled"] else "Enable"}</button></form></td><td>{remove}</td></tr>'
        ann_rows="".join(f'<div class="announcement-admin-row"><div><strong>{esc(a["title"])}</strong><small>{esc(a["app_name"])} · {esc(a["status"])}</small></div><form method="post" action="/admin/announcements/delete"><input type="hidden" name="csrf" value="{esc(session["csrf_token"])}"><input type="hidden" name="id" value="{a["id"]}"><button class="btn danger compact-btn">Remove</button></form></div>' for a in announcements)
        log_rows="".join(f'<tr><td>{esc(l["created_at"][:19].replace("T"," "))}</td><td>{esc(l["event_type"])}</td><td>{esc(l["user_email"])}</td><td>{esc(l["app_name"] or "Workspace")}</td><td>{esc(l["status"])}</td></tr>' for l in logs)
        def role_form(u):
            if u["email"] == user["email"]: return esc(u["role"])
            opts=f'<option value="Employee" {"selected" if u["role"]=="Employee" else ""}>Employee</option><option value="Administrator" {"selected" if u["role"]=="Administrator" else ""}>Administrator</option>'
            return f'<form class="settings-form" method="post" action="/admin/users/role"><input type="hidden" name="csrf" value="{esc(session["csrf_token"])}"><input type="hidden" name="id" value="{u["id"]}"><select name="role">{opts}</select><button class="btn secondary compact-btn">Save</button></form>'
        user_rows="".join(f'<tr><td>{esc(u["employee_id"])}</td><td>{esc(u["name"])}</td><td>{esc(u["email"])}</td><td>{role_form(u)}</td><td>{esc(u["department"])}</td></tr>' for u in users_list)
        form=f'<section id="publish" class="tab-pane active panel"><h2>Add an application</h2><form class="grid-form" method="post" action="/admin/apps/create"><input type="hidden" name="csrf" value="{esc(session["csrf_token"])}"><div class="field"><label>Application name</label><input name="name" required></div><div class="field"><label>Unique slug</label><input name="slug" required pattern="[a-z0-9-]+"></div><div class="field full"><label>Description</label><textarea name="description" required></textarea></div><div class="field"><label>Category</label><select name="category"><option>productivity</option><option>hr</option><option>finance</option><option>operations</option><option>performance</option><option>custom</option></select></div><div class="field"><label>SSO protocol</label><select name="sso_mode"><option>oidc</option><option>saml2</option><option>jwt_header</option><option>shared_session</option><option>oauth2</option></select></div><div class="field"><label>Application URL</label><input name="url" required placeholder="https://app.company.com"></div><div class="field"><label>Version</label><input name="version" value="v1.0.0"></div><div class="field"><label>Publisher</label><input name="publisher" value="Vtab IT"></div><div class="field"><label>Brand color and hex code</label><div class="color-control"><input id="brand-color-picker" type="color" value="#5b5ce2"><input id="brand-color-code" name="color_code" value="#5B5CE2" pattern="#[0-9A-Fa-f]{{6}}" required></div><div class="color-preview"><span id="brand-color-swatch" class="color-preview-swatch"></span><span>Enter an exact 6-digit hex color.</span></div></div><div class="field"><label>Fallback icon initials</label><input name="icon" value="AP" maxlength="3"></div><div class="field full"><label>Custom logo URL or data image</label><div class="logo-uploader"><div class="logo-preview"><img id="app-logo-preview" hidden alt="Logo preview"><span>Logo preview</span></div><div><div class="logo-controls"><input id="app-logo-file" type="file" accept="image/*"><input id="app-logo-value" name="logo_url" placeholder="HTTPS image URL"></div><div class="field-help">Uploaded images must be smaller than 300 KB.</div></div></div></div><div class="field full"><label>Visibility</label><div class="visibility-picker"><label class="visibility-option"><input type="radio" name="visibility" value="everyone" checked><span><strong>Everyone</strong><small>General launcher</small></span></label><label class="visibility-option"><input type="radio" name="visibility" value="admins"><span><strong>Administrators only</strong><small>Protected admin launcher</small></span></label></div></div><button class="btn">Add application</button></form></section>'
        upcoming=f'<section id="upcoming" class="tab-pane panel"><h2>Publish upcoming application or update</h2><form class="grid-form" method="post" action="/admin/announcements/create"><input type="hidden" name="csrf" value="{esc(session["csrf_token"])}"><div class="field"><label>Headline</label><input name="title" required></div><div class="field"><label>Application name</label><input name="app_name" required></div><div class="field"><label>Version</label><input name="version" value="v1.0 Beta"></div><div class="field"><label>Status</label><select name="status"><option>Coming Soon</option><option>Beta Testing</option><option>Planned</option><option>Live Now</option></select></div><div class="field"><label>Expected release</label><input name="release_date" placeholder="Q4 2026"></div><div class="field"><label>Progress percentage</label><input type="number" min="0" max="100" name="progress_percent" value="0"></div><div class="field full"><label>Description</label><textarea name="description" required></textarea></div><div class="field full"><label>Highlights separated by |</label><input name="highlights"></div><button class="btn">Publish release information</button></form><div class="announcement-list">{ann_rows}</div></section>'
        content=f'<section class="panel admin-hero"><div><div class="eyebrow">Administration</div><h1>Application settings</h1><p>Add applications, control visibility and publish releases.</p></div><a class="btn secondary page-home" href="/">{nav_icon("home")}Home</a></section><div data-tabs><div class="tabs"><button class="tab active" data-tab="publish">Add application</button><button class="tab" data-tab="manage">Manage &amp; visibility</button><button class="tab" data-tab="users">Manage users</button><button class="tab" data-tab="upcoming">Upcoming releases</button><button class="tab" data-tab="audit">Audit trail</button></div>{form}<section id="manage" class="tab-pane panel"><h2>Manage applications</h2><div class="table-wrap"><table><thead><tr><th>Application</th><th>Category</th><th>Visibility</th><th>Status</th><th>Actions</th></tr></thead><tbody>{app_rows}</tbody></table></div></section><section id="users" class="tab-pane panel"><h2>Manage users</h2><div class="table-wrap"><table><thead><tr><th>Emp ID</th><th>Name</th><th>Email</th><th>Role</th><th>Department</th></tr></thead><tbody>{user_rows}</tbody></table></div></section>{upcoming}<section id="audit" class="tab-pane panel"><h2>Security audit trail</h2><div class="table-wrap"><table><thead><tr><th>Time</th><th>Event</th><th>User</th><th>App</th><th>Status</th></tr></thead><tbody>{log_rows}</tbody></table></div></section></div>'
        return self.layout("Application settings",content,user,session,"admin",query)

    def app_page(self,slug,user,session,query):
        with db() as con: app=con.execute("SELECT * FROM applications WHERE slug=%s AND enabled=1 AND (visibility='everyone' OR %s='Administrator')",(slug,user["role"])).fetchone()
        if not app: return self.layout("Not found",'<div class="panel"><h2>Application unavailable</h2></div>',user,session,"home",query)
        self.audit("APP_LAUNCH",user["email"],"Application opened.",app["name"])
        header=f'<section class="app-header"><div><div class="sso">Secure single sign-on · {esc(app["sso_mode"].upper())}</div><h1>{esc(app["name"])}</h1><p>{esc(app["description"])}</p></div>{product_icon(app)}</section>'
        if app["url"] and app["url"].startswith("http"):
            launch_url = f"/api/sso/token?app={esc(app['slug'])}" if app["sso_mode"] == "vtab_assertion" else esc(app["url"])
            body=f'<div class="panel"><h2>Ready to launch</h2><p>Vtab will open this registered application using your workspace identity.</p><a class="btn" href="{launch_url}" target="_blank" rel="noopener">Open application</a></div>'
        elif slug=="hr-portal":
            with db() as con: requests=con.execute("SELECT * FROM leave_requests WHERE user_id=%s ORDER BY id DESC",(user["id"],)).fetchall()
            body=f'<div class="metric-grid"><div class="panel metric"><small>Department</small><strong>{esc(user["department"])}</strong></div><div class="panel metric"><small>Employee ID</small><strong>{esc(user["employee_id"])}</strong></div><div class="panel metric"><small>Requests</small><strong>{len(requests)}</strong></div></div><div class="panel"><h2>Request leave</h2><form class="grid-form" method="post" action="/leave"><input type="hidden" name="csrf" value="{esc(session["csrf_token"])}"><div class="field"><label>Leave type</label><select name="leave_type"><option>Annual Leave</option><option>Sick Leave</option></select></div><div class="field"><label>Start date</label><input type="date" name="start_date" required></div><div class="field"><label>End date</label><input type="date" name="end_date" required></div><div class="field"><label>Reason</label><input name="reason"></div><button class="btn">Submit request</button></form></div>'
        elif slug=="appraisal":
            body=f'<div class="panel"><h2>Self-appraisal</h2><form class="grid-form" method="post" action="/appraisal"><input type="hidden" name="csrf" value="{esc(session["csrf_token"])}"><div class="field"><label>Quarter</label><select name="quarter"><option>Q3 2026</option><option>Q4 2026</option></select></div><div class="field full"><label>Achievements and feedback</label><textarea name="feedback" minlength="20" required></textarea></div><button class="btn">Submit appraisal</button></form></div>'
        elif slug=="payroll":
            with db() as con: pay=con.execute("SELECT * FROM payroll_records WHERE user_id=%s ORDER BY id DESC LIMIT 1",(user["id"],)).fetchone()
            net=float(pay["base_salary"])+float(pay["housing"])+float(pay["bonus"])-float(pay["tax"])-float(pay["insurance"]) if pay else 0
            body=f'<div class="metric-grid"><div class="panel metric"><small>Pay period</small><strong>{esc(pay["month"] if pay else "-")}</strong></div><div class="panel metric"><small>Net pay</small><strong>${net:,.2f}</strong></div><div class="panel metric"><small>Payment date</small><strong>{esc(pay["payment_date"] if pay else "-")}</strong></div></div><a class="btn" href="/payroll/download">Download payslip PDF</a>'
        elif slug=="meet-assistant":
            body='<div class="panel"><h2>Meet Assistant</h2><p>Capture agendas, decisions, searchable notes and assigned follow-up actions from one workspace.</p><div class="highlight-list"><span>Live notes</span><span>Action items</span><span>Searchable summaries</span></div></div>'
        else: body='<div class="panel"><h2>Workspace application</h2><p>This application is connected to your Vtab identity.</p></div>'
        return self.layout(app["name"],header+body,user,session,"home",query)

    def do_GET(self):
        path,query=self.route()
        if path=="/assets/style.css": return self.send_bytes((BASE_DIR/"style.css").read_bytes(),content_type="text/css; charset=utf-8")
        if path=="/assets/app.js": return self.send_bytes((BASE_DIR/"app.js").read_bytes(),content_type="application/javascript; charset=utf-8")
        if path=="/logo.png": return self.send_bytes((BASE_DIR/"public"/"logo.png").read_bytes(), content_type="image/png")
        if path=="/favicon.ico": return self.send_bytes((BASE_DIR/"public"/"logo.png").read_bytes(), content_type="image/png")
        if path=="/health": return self.text(json.dumps({"status":"ok","python":"source-runtime","database":"supabase-postgresql"}),content_type="application/json")
        if path=="/login":
            user,_=self.current_session(); return self.redirect("/") if user else self.text(self.login_page(query))
        if path=="/verify-otp":
            user,_=self.current_session(); return self.redirect("/") if user else self.text(self.verify_otp_page(query))
        if path=="/register":
            content=f'<div class="login-page"><div class="login-card"><img class="brandmark" src="/logo.png" alt="VTAB 365"><h1>Create your Vtab identity</h1><form method="post" action="/register" class="grid-form"><div class="field full"><label>Full name</label><input name="name" required></div><div class="field full"><label>Work email</label><input type="email" name="email" required></div><div class="field"><label>Department</label><input name="department" required></div><div class="field"><label>Employee ID</label><input name="employee_id" required></div><div class="field full"><label>Password</label><input type="password" name="password" minlength="8" required></div><button class="btn">Create employee account</button></form><p><a href="/login">Back to sign in</a></p></div></div>'; return self.text(self.layout("Register",content))
        user,session=self.require_user()
        if not user: return
        if path=="/": return self.text(self.dashboard(user,session,query))
        if path=="/apps": return self.text(self.apps_page(user,session,query))
        if path=="/updates": return self.text(self.updates_page(user,session,query))
        if path=="/quick-access": return self.text(self.quick_page(user,session,query))
        if path=="/sso": return self.text(self.sso_page(user,session,query))
        if path=="/admin-apps": return self.text(self.admin_apps_page(user,session,query)) if user["role"]=="Administrator" else self.text(self.layout("Forbidden",'<div class="panel"><h2>Administrator access required</h2></div>',user,session),403)
        if path=="/admin": return self.text(self.admin_page(user,session,query)) if user["role"]=="Administrator" else self.text(self.layout("Forbidden",'<div class="panel"><h2>Administrator access required</h2></div>',user,session),403)
        if path.startswith("/app/"): return self.text(self.app_page(urllib.parse.unquote(path[5:]),user,session,query))
        if path=="/api/apps":
            with db() as con: rows=con.execute("SELECT id,slug,name,description,category,url,sso_mode,enabled,version,publisher,visibility FROM applications WHERE enabled=1 AND (visibility='everyone' OR %s='Administrator') ORDER BY name",(user["role"],)).fetchall()
            return self.text(json.dumps({"applications":[dict(r) for r in rows]},indent=2),content_type="application/json")
        if path=="/payroll/download": return self.download_payslip(user)
        if path=="/api/sso/token":
            app_slug = query.get("app", [""])[0]
            if not app_slug: return self.text(self.layout("SSO Error", "<div class='panel'><h2>Missing application identifier</h2></div>", user, session), 400)
            with db() as con:
                app_record = con.execute("SELECT * FROM applications WHERE slug=%s AND enabled=1", (app_slug,)).fetchone()
            if not app_record: return self.text(self.layout("SSO Error", "<div class='panel'><h2>Application not found or disabled</h2></div>", user, session), 404)
            sso_secret = os.getenv("VTAB_SSO_SECRET")
            if not sso_secret: return self.text(self.layout("SSO Error", "<div class='panel'><h2>SSO not configured (missing secret)</h2></div>", user, session), 500)
            
            import uuid
            payload = {
                "iss": "vtab360",
                "aud": app_slug,
                "purpose": "vtab_sso",
                "employee_id": user["employee_id"],
                "email": user["email"],
                "name": user["name"],
                "iat": int(datetime.now(timezone.utc).timestamp()),
                "exp": int((datetime.now(timezone.utc) + timedelta(minutes=2)).timestamp()),
                "jti": str(uuid.uuid4())
            }
            def b64url(b): return base64.urlsafe_b64encode(b).replace(b'=', b'').decode('ascii')
            header = b64url(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
            payload_str = b64url(json.dumps(payload).encode())
            signature = b64url(hmac.new(sso_secret.encode(), f"{header}.{payload_str}".encode(), hashlib.sha256).digest())
            assertion = f"{header}.{payload_str}.{signature}"
            
            self.audit("SSO_LOGIN", user["email"], f"Generated SSO assertion for {app_slug}.", app=app_slug)
            
            target_url = app_record["url"]
            sep = "&" if "?" in target_url else "?"
            redirect_url = f"{target_url}{sep}token={urllib.parse.quote(assertion)}"
            return self.redirect(redirect_url)
            
        return self.text(self.layout("Not found",'<div class="panel"><h2>Page not found</h2><a href="/">Return home</a></div>',user,session),404)

    def do_POST(self):
        path,_=self.route(); form=self.form()
        if path=="/login":
            login_email = form.get("email","").strip()
            login_password = form.get("password","")
            with db() as con: user=con.execute("SELECT * FROM users WHERE email=%s AND active=1",(login_email,)).fetchone()
            if not user or not password_ok(login_password,user["password_hash"]): 
                self.audit("LOGIN",form.get("email","anonymous"),"Invalid credentials.",status="FAILED"); return self.flash("/login","Invalid email or password.",True)
            import random
            otp = str(random.randint(100000, 999999))
            with db() as con: con.execute("INSERT INTO login_otps (email, otp_code) VALUES (%s, %s)", (user["email"], otp))
            send_email_otp(user["email"], otp)
            self.send_response(303)
            self.send_header("Location", "/verify-otp")
            import urllib.parse
            self.send_header("Set-Cookie", f"vtab_pending_email={urllib.parse.quote(user['email'])}; Path=/; HttpOnly; Max-Age=300")
            self.end_headers()
            return
        if path=="/verify-otp":
            import urllib.parse
            cookies_dict = {}
            if "Cookie" in self.headers:
                c = cookies.SimpleCookie(self.headers["Cookie"])
                cookies_dict = {k: v.value for k, v in c.items()}
            pending_email = cookies_dict.get("vtab_pending_email")
            if pending_email: pending_email = urllib.parse.unquote(pending_email)
            if not pending_email: return self.flash("/login", "Session expired. Please log in again.", True)
            otp_code = form.get("otp_code", "").strip()
            with db() as con:
                otp_record = con.execute("SELECT * FROM login_otps WHERE email=%s AND otp_code=%s AND created_at >= NOW() - INTERVAL '5 minutes' ORDER BY created_at DESC LIMIT 1", (pending_email, otp_code)).fetchone()
                if not otp_record:
                    return self.flash("/verify-otp", "Invalid or expired verification code.", True)
                con.execute("DELETE FROM login_otps WHERE email=%s", (pending_email,))
                user = con.execute("SELECT * FROM users WHERE email=%s AND active=1", (pending_email,)).fetchone()
            self.audit("LOGIN",user["email"],"Workspace session created.")
            return self.redirect("/",self.new_session(user["id"]))
        if path=="/register":
            name,email,password=form.get("name","").strip(),form.get("email","").strip().lower(),form.get("password","")
            if not name or "@" not in email or len(password)<8: return self.flash("/register","Enter valid registration details.",True)
            try:
                with db() as con:
                    uid=con.execute("INSERT INTO users(name,email,password_hash,role,department,employee_id,registered_at) VALUES(%s,%s,%s,'Employee',%s,%s,%s) RETURNING id",(name,email,password_hash(password),form.get("department","General"),form.get("employee_id",""),datetime.now().date().isoformat())).fetchone()["id"]
            except sqlite3.IntegrityError: return self.flash("/register","Email or employee ID already exists.",True)
            return self.redirect("/",self.new_session(uid))
        user,session=self.require_user()
        if not user: return
        if not self.check_csrf(form,session): return self.text(self.layout("Invalid request",'<div class="panel"><h2>Security check failed</h2></div>',user,session),403)
        if path=="/logout":
            with db() as con: con.execute("DELETE FROM sessions WHERE id=%s",(session["id"],))
            return self.redirect("/login",f"{COOKIE_NAME}=; Path=/; Max-Age=0")
        if path=="/quick-access/save":
            ids=[int(k[4:]) for k in form if k.startswith("app_") and k[4:].isdigit()][:6]
            with db() as con:
                allowed={r["id"] for r in con.execute("SELECT id FROM applications WHERE enabled=1 AND (visibility='everyone' OR %s='Administrator')",(user["role"],)).fetchall()}
                con.execute("DELETE FROM user_quick_access WHERE user_id=%s",(user["id"],))
                con.executemany("INSERT INTO user_quick_access(user_id,app_id,position) VALUES(%s,%s,%s)",[(user["id"],i,p) for p,i in enumerate(ids) if i in allowed])
            return self.flash("/quick-access","Quick Access updated.")
        if path=="/leave":
            start,end=form.get("start_date",""),form.get("end_date","")
            if not start or not end or end<start: return self.flash("/app/hr-portal","End date must be after the start date.",True)
            with db() as con: con.execute("INSERT INTO leave_requests(user_id,leave_type,start_date,end_date,reason,status,created_at) VALUES(%s,%s,%s,%s,%s,'Pending',%s)",(user["id"],form.get("leave_type","Annual Leave"),start,end,form.get("reason","")[:250],now_iso()))
            return self.flash("/app/hr-portal","Leave request submitted.")
        if path=="/appraisal":
            feedback=form.get("feedback","").strip()
            if len(feedback)<20: return self.flash("/app/appraisal","Please provide at least 20 characters.",True)
            with db() as con: con.execute("INSERT INTO appraisals(user_id,quarter,feedback,created_at) VALUES(%s,%s,%s,%s)",(user["id"],form.get("quarter","Q3 2026"),feedback[:5000],now_iso()))
            return self.flash("/app/appraisal","Self-appraisal submitted.")
        if not path.startswith("/admin/") or user["role"]!="Administrator": return self.text("Forbidden",403)
        if path=="/admin/apps/create":
            slug=form.get("slug","").strip().lower(); color=form.get("color_code","#5B5CE2").strip(); visibility=form.get("visibility","everyone"); logo=form.get("logo_url","").strip()
            if not slug or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in slug): return self.flash("/admin","Invalid slug.",True)
            if len(color)!=7 or not color.startswith("#") or any(c not in "0123456789abcdefABCDEF" for c in color[1:]): return self.flash("/admin","Invalid hex color.",True)
            if visibility not in {"everyone","admins"}: visibility="everyone"
            if logo and not logo.startswith(("https://","data:image/")): return self.flash("/admin","Logo must be HTTPS or an uploaded image.",True)
            try:
                with db() as con: con.execute("INSERT INTO applications(slug,name,description,category,icon,color,url,sso_mode,enabled,built_in,allowed_roles,version,publisher,created_at,visibility,logo_url) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,1,0,%s,%s,%s,%s,%s,%s)",(slug,form.get("name","")[:80],form.get("description","")[:400],form.get("category","custom"),form.get("icon","AP")[:3].upper(),color.upper(),form.get("url","")[:500],form.get("sso_mode","oidc"),'["All Employees"]',form.get("version","v1.0.0")[:30],form.get("publisher","Vtab IT")[:100],now_iso(),visibility,logo))
            except sqlite3.IntegrityError: return self.flash("/admin","Application slug already exists.",True)
            return self.flash("/admin","Application added.")
        if path=="/admin/apps/settings":
            visibility=form.get("visibility","everyone"); visibility=visibility if visibility in {"everyone","admins"} else "everyone"
            with db() as con: con.execute("UPDATE applications SET visibility=%s WHERE id=%s",(visibility,form.get("id")))
            return self.flash("/admin?tab=manage","Visibility updated.")
        if path=="/admin/users/role":
            role=form.get("role","Employee"); role=role if role in {"Employee","Administrator"} else "Employee"
            with db() as con: con.execute("UPDATE users SET role=%s WHERE id=%s",(role,form.get("id")))
            return self.flash("/admin?tab=users","User role updated.")
        if path=="/admin/apps/toggle":
            with db() as con: con.execute("UPDATE applications SET enabled=CASE enabled WHEN 1 THEN 0 ELSE 1 END WHERE id=%s",(form.get("id"),))
            return self.flash("/admin?tab=manage","Application status updated.")
        if path=="/admin/apps/delete":
            with db() as con: con.execute("DELETE FROM applications WHERE id=%s AND built_in=0",(form.get("id"),))
            return self.flash("/admin?tab=manage","Application removed.")
        if path=="/admin/announcements/create":
            try: progress=max(0,min(100,int(form.get("progress_percent","0") or 0)))
            except ValueError: progress=0
            with db() as con: con.execute("INSERT INTO announcements(title,app_name,version,description,status,created_at,release_date,highlights,progress_percent) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",(form.get("title","")[:120],form.get("app_name","")[:100],form.get("version","v1.0")[:40],form.get("description","")[:600],form.get("status","Coming Soon"),now_iso(),form.get("release_date","")[:80],form.get("highlights","")[:500],progress))
            return self.flash("/admin?tab=upcoming","Release information published.")
        if path=="/admin/announcements/delete":
            with db() as con: con.execute("DELETE FROM announcements WHERE id=%s",(form.get("id"),))
            return self.flash("/admin?tab=upcoming","Release information removed.")
        return self.text("Not found",404)

    def download_payslip(self,user):
        with db() as con: pay=con.execute("SELECT * FROM payroll_records WHERE user_id=%s ORDER BY id DESC LIMIT 1",(user["id"],)).fetchone()
        if not pay: return self.text("No payroll record",404)
        net=float(pay["base_salary"])+float(pay["housing"])+float(pay["bonus"])-float(pay["tax"])-float(pay["insurance"])
        lines=["VTAB OFFICE SUITE 365 - PAYSLIP",f"Employee: {user['name']} ({user['employee_id']})",f"Period: {pay['month']}","",f"Basic salary: ${float(pay['base_salary']):,.2f}",f"Housing: ${float(pay['housing']):,.2f}",f"Bonus: ${float(pay['bonus']):,.2f}",f"Tax: -${float(pay['tax']):,.2f}",f"Insurance: -${float(pay['insurance']):,.2f}",f"NET PAY: ${net:,.2f}"]
        def pe(s): return s.replace("\\","\\\\").replace("(","\\(").replace(")","\\)")
        commands=["BT","/F1 17 Tf","55 780 Td",f"({pe(lines[0])}) Tj","/F1 11 Tf"]
        for line in lines[1:]: commands += ["0 -25 Td",f"({pe(line)}) Tj"]
        commands.append("ET"); stream="\n".join(commands).encode("latin-1","replace")
        objects=[b"<< /Type /Catalog /Pages 2 0 R >>",b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",f"<< /Length {len(stream)} >>\nstream\n".encode()+stream+b"\nendstream",b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
        out=bytearray(b"%PDF-1.4\n"); offsets=[0]
        for i,obj in enumerate(objects,1): offsets.append(len(out)); out.extend(f"{i} 0 obj\n".encode()+obj+b"\nendobj\n")
        xref=len(out); out.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode())
        for off in offsets[1:]: out.extend(f"{off:010d} 00000 n \n".encode())
        out.extend(f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode())
        return self.send_bytes(bytes(out),content_type="application/pdf",headers={"Content-Disposition":'attachment; filename="vtab-payslip.pdf"'})


if __name__ == "__main__":
    if False:
        raise RuntimeError("DATABASE_URL environment variable is not set. "
                           "Get the connection string from Supabase Dashboard → "
                           "Project Settings → Database → Connection string (URI).")
    import time as _time
    for _attempt in range(30):
        try:
            init_database()
            break
        except Exception as _e:
            if _attempt == 29:
                raise
            print(f"[VTAB] DB not ready yet ({_e}). Retrying in 10 seconds... (attempt {_attempt+1}/30)")
            _time.sleep(10)
    print("Vtab Office Suite 365 V7 — PostgreSQL (Supabase) edition")
    print(f"Database: Supabase PostgreSQL")
    print(f"Open http://{HOST}:{PORT} in your browser")
    if SECRET_KEY == b"vtab-local-development-key-change-me":
        print("Development mode: set VTAB_SECRET_KEY before production use.")
    try: ThreadingHTTPServer((HOST,PORT),VtabHandler).serve_forever()
    except KeyboardInterrupt: print("\nServer stopped.")

