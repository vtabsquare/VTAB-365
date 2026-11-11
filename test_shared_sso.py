"""Isolated regression suite; uses an in-memory database double, never Supabase."""
import base64
from contextlib import contextmanager
from datetime import datetime, timezone
from email.message import Message
import hashlib
import hmac
import http.client
from http.server import ThreadingHTTPServer
import io
import json
import sys
import threading
import types
import unittest
from unittest.mock import patch

# App's PostgreSQL adapter is not exercised here. No real connection is allowed.
driver = types.ModuleType("psycopg2")
driver.connect = lambda *a, **kw: (_ for _ in ()).throw(AssertionError("Real DB forbidden"))
extras = types.ModuleType("psycopg2.extras")
extras.RealDictCursor = object
with patch.dict(sys.modules, {"psycopg2": driver, "psycopg2.extras": extras}):
    import app
from vtab_identity import *
from vtab_sso_middleware import VtabAuthenticator, VtabSSOMiddleware

KEY = b"test-only-random-secret-key-of-32-bytes-minimum"
USER = dict(id=15, email="employee@example.test", name="Example Employee", role="Administrator", employee_id="EMP015", active=1)


class FakeDB:
    def __init__(self):
        self.user = dict(USER)
        self.sessions = {}
        self.row = None

    @contextmanager
    def connect(self):
        yield self

    def execute(self, sql, args=()):
        if sql.startswith("INSERT INTO sessions"):
            sid, uid, csrf, created, expires = args
            self.sessions[sid] = dict(id=sid, user_id=uid, csrf_token=csrf, created_at=created, expires_at=expires)
            self.row = None
        elif sql.startswith("SELECT * FROM sessions"):
            self.row = self.sessions.get(args[0])
            if self.row and self.row["expires_at"] <= args[1]:
                self.row = None
        elif sql.startswith("SELECT * FROM users"):
            self.row = self.user if self.user["active"] and self.user["id"] == args[0] else None
        elif sql.startswith("DELETE FROM sessions WHERE id="):
            self.sessions.pop(args[0], None)
            self.row = None
        else:
            raise AssertionError(sql)
        return self

    def fetchone(self):
        return self.row


class IdentityTests(unittest.TestCase):
    def test_round_trip_and_expiry(self):
        token = issue_vtab_token(USER, "session", 200, KEY, now=100)
        self.assertEqual(verify_vtab_token(token, KEY, now=101)["employee_id"], "EMP015")
        self.assertIsNone(verify_vtab_token(token, KEY, now=200))
        self.assertIsNone(verify_vtab_token(token, KEY, now=99))
        self.assertIsNone(verify_vtab_token(token, b"x" * 32, now=101))

    def test_tampering_and_malformed(self):
        token = issue_vtab_token(USER, "session", 200, KEY, now=100)
        for value in (None, "", "a.b.c", "x" * 5000, "☃.x.y", token.replace(".", ".x", 1)):
            with self.subTest(value=str(value)[:20]):
                self.assertIsNone(verify_vtab_token(value, KEY, now=101))

    def test_claims_and_algorithm(self):
        token = issue_vtab_token(USER, "session", 200, KEY, now=100)
        head, body, _ = token.split(".")
        data = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        def signed(h, payload):
            b = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
            message = h + "." + b
            return message + "." + base64.urlsafe_b64encode(hmac.new(KEY, message.encode(), hashlib.sha256).digest()).rstrip(b"=").decode()
        for field, value in (("iss", "bad"), ("aud", "bad"), ("purpose", "bad"), ("exp", True), ("exp", 999999), ("sid", None), ("role", "Demo")):
            with self.subTest(field=field):
                self.assertIsNone(verify_vtab_token(signed(head, dict(data, **{field: value})), KEY, now=101))
        wrong = base64.urlsafe_b64encode(b'{"alg":"none","typ":"JWT"}').rstrip(b"=").decode()
        self.assertIsNone(verify_vtab_token(signed(wrong, data), KEY, now=101))

    def test_cookie_scope(self):
        for host in ("vtab360.vtabsquare.com", "sales.vtabsquare.com:443", "vtabsquare.com"):
            value = cookie_header("test", "value", host)
            self.assertIn("Domain=.vtabsquare.com", value)
            self.assertIn("Secure", value)
            self.assertIn("HttpOnly", value)
            self.assertIn("SameSite=Lax", value)
        for host in ("localhost:8000", "127.0.0.1:8003", "vtabsquare.com.attacker.test", "evilvtabsquare.com"):
            self.assertNotIn("Domain=", cookie_header("test", "value", host))

    def test_duplicate_cookie_rejected(self):
        self.assertIsNone(read_cookie("vtab_identity=a; vtab_identity=b", IDENTITY_COOKIE))
        self.assertEqual(read_cookie("other=x; vtab_identity=a", IDENTITY_COOKIE), "a")

    def test_weak_secret_rejected(self):
        for key in (DEVELOPMENT_KEY, b"", b"short"):
            with self.assertRaises(ValueError):
                issue_vtab_token(USER, "s", 200, key, now=100)


class PortalTests(unittest.TestCase):
    def setUp(self):
        self.db = FakeDB()
        self.patches = [patch.object(app, "db", self.db.connect), patch.object(app, "SECRET_KEY", KEY)]
        for p in self.patches: p.start()
        self.handler = object.__new__(app.VtabHandler)
        self.handler.headers = Message()
        self.handler.headers["Host"] = "vtab360.vtabsquare.com"

    def tearDown(self):
        for p in reversed(self.patches): p.stop()

    def token(self):
        headers = self.handler.new_session(15, federated=True)
        jar = SimpleCookie()
        for header in headers: jar.load(header)
        return jar[IDENTITY_COOKIE].value, jar["vtab_session"].value

    def test_issuance_migration_and_legacy(self):
        token, session = self.token()
        self.assertEqual(verify_vtab_token(token, KEY)["sub"], "15")
        self.handler.headers["Cookie"] = "vtab_session=" + session
        self.assertEqual(self.handler.current_session()[0]["id"], 15)
        cleared = self.handler.clear_auth_cookies()
        self.assertEqual(sum("vtab_session=" in h for h in cleared), 2)
        self.assertEqual(sum("vtab_identity=" in h for h in cleared), 2)
        self.assertTrue(all("Max-Age=0" in h for h in cleared))

    def test_demo_and_registration_not_federated(self):
        self.db.user["role"] = "Demo"
        headers = self.handler.new_session(15, federated=True)
        self.assertFalse(any(h.startswith("vtab_identity=") and "Max-Age=43200" in h for h in headers))
        self.assertFalse(any(h.startswith("vtab_session=") and "Domain=" in h and "Max-Age=43200" in h for h in headers))
        self.db.user["role"] = "Employee"
        self.assertFalse(any(h.startswith("vtab_identity=") and "Max-Age=43200" in h for h in self.handler.new_session(15)))

    def test_local_development_without_secret(self):
        self.handler.headers.replace_header("Host", "localhost:8000")
        with patch.object(app, "SECRET_KEY", DEVELOPMENT_KEY):
            self.assertTrue(self.handler.new_session(15, federated=True))

    def test_http_online_revocation_and_live_role(self):
        token, session = self.token()
        server = ThreadingHTTPServer(("127.0.0.1", 0), app.VtabHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            auth = VtabAuthenticator(KEY, verify_url=f"http://127.0.0.1:{server.server_port}/api/auth/verify")
            cookie = "vtab_identity=" + token
            self.assertEqual(auth.authenticate(cookie)["role"], "Administrator")
            self.db.user["role"] = "Employee"
            self.assertEqual(auth.authenticate(cookie)["role"], "Employee")
            self.db.user["active"] = 0
            self.assertIsNone(auth.authenticate(cookie))
            self.db.user["active"] = 1
            # Exercise the actual CSRF-protected logout route with real HTTP headers.
            sid = verify_vtab_token(token, KEY)["sid"]
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port)
            body = "csrf=" + self.db.sessions[sid]["csrf_token"]
            connection.request("POST", "/logout", body, {"Host": "vtab360.vtabsquare.com", "Cookie": "vtab_session=" + session})
            response = connection.getresponse()
            self.assertEqual(response.status, 303)
            self.assertEqual(len(response.headers.get_all("Set-Cookie")), 5)
            response.read(); connection.close()
            self.assertIsNone(auth.authenticate(cookie))
        finally:
            server.shutdown(); server.server_close(); thread.join()

    def test_database_failure_is_503(self):
        token, _ = self.token()
        self.handler.headers["Authorization"] = "Bearer " + token
        with patch.object(app, "db", side_effect=RuntimeError("Unavailable")), patch.object(self.handler, "text") as result:
            self.handler.verify_identity()
            self.assertEqual(result.call_args.args[1], 503)

    def test_wsgi_authentication(self):
        token, _ = self.token()
        def protected(environ, start):
            start("200 OK", [])
            return [environ["REMOTE_USER"].encode()]
        middleware = VtabSSOMiddleware(protected, secret=KEY, online=False)
        status = []
        self.assertEqual(middleware({"PATH_INFO": "/", "HTTP_COOKIE": "vtab_identity=" + token}, lambda s, h: status.append(s)), [USER["email"].encode()])
        self.assertEqual(status[-1], "200 OK")
        middleware({"PATH_INFO": "/"}, lambda s, h: status.append(s))
        self.assertEqual(status[-1], "401 Unauthorized")


if __name__ == "__main__":
    unittest.main()
