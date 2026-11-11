"""Shared VTAB identity codec. Standard-library-only HS256 JWTs."""
import base64
import hashlib
import hmac
import json
import time
import urllib.parse
from http.cookies import SimpleCookie, CookieError

ISSUER = "https://vtab360.vtabsquare.com"
AUDIENCE = "vtab-square-apps"
IDENTITY_COOKIE = "vtab_identity"
DEVELOPMENT_KEY = b"vtab-local-development-key-change-me"
MAX_LIFETIME = 43200


def production_host(host):
    try:
        name = urllib.parse.urlsplit("//" + host).hostname or ""
        return name == "vtabsquare.com" or name.endswith(".vtabsquare.com")
    except ValueError:
        return False


def cookie_header(name, value, host, max_age=MAX_LIFETIME, shared=True):
    jar = SimpleCookie()
    jar[name] = value
    item = jar[name]
    item["path"] = "/"
    item["httponly"] = True
    item["samesite"] = "Lax"
    item["max-age"] = max_age
    if production_host(host):
        item["secure"] = True
        if shared:
            item["domain"] = ".vtabsquare.com"
    if max_age == 0:
        item["expires"] = "Thu, 01 Jan 1970 00:00:00 GMT"
    return item.OutputString()


def read_cookie(header, name):
    # Duplicate cookie names can result from legacy host-only cookies. Fail closed.
    if sum(part.strip().split("=", 1)[0] == name for part in header.split(";")) != 1:
        return None
    try:
        jar = SimpleCookie(header)
        return jar[name].value if name in jar else None
    except CookieError:
        return None


def _encode(value):
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _decode(value):
    return base64.b64decode(value + "=" * (-len(value) % 4), altchars=b"-_", validate=True)


def require_secret(secret):
    if not isinstance(secret, bytes) or len(secret) < 32 or secret == DEVELOPMENT_KEY:
        raise ValueError("Shared sign-in requires a random VTAB_SECRET_KEY of at least 32 bytes")


def issue_vtab_token(user, session_id, expires_at, secret, now=None):
    require_secret(secret)
    issued = int(time.time() if now is None else now)
    payload = {key: user[key] for key in ("email", "name", "role", "employee_id")}
    payload.update(iss=ISSUER, aud=AUDIENCE, purpose="vtab_identity", sub=str(user["id"]),
                   sid=session_id, iat=issued, exp=min(int(expires_at), issued + MAX_LIFETIME))
    header = _encode(b'{"alg":"HS256","typ":"JWT"}')
    body = _encode(json.dumps(payload, separators=(",", ":")).encode())
    signed = header + "." + body
    return signed + "." + _encode(hmac.new(secret, signed.encode("ascii"), hashlib.sha256).digest())


def verify_vtab_token(token, secret, now=None):
    try:
        require_secret(secret)
        if not isinstance(token, str) or len(token) > 4096:
            return None
        head, body, signature = token.split(".")
        expected = hmac.new(secret, (head + "." + body).encode("ascii"), hashlib.sha256).digest()
        if not hmac.compare_digest(_decode(signature), expected):
            return None
        if json.loads(_decode(head)) != {"alg": "HS256", "typ": "JWT"}:
            return None
        payload = json.loads(_decode(body))
        if not isinstance(payload, dict):
            return None
        current = int(time.time() if now is None else now)
        if type(payload.get("exp")) is not int or type(payload.get("iat")) is not int:
            return None
        if not payload["iat"] <= current < payload["exp"] <= payload["iat"] + MAX_LIFETIME:
            return None
        if (payload.get("iss"), payload.get("aud"), payload.get("purpose")) != (ISSUER, AUDIENCE, "vtab_identity"):
            return None
        for key in ("sub", "sid", "email", "name", "role", "employee_id"):
            if not isinstance(payload.get(key), str):
                return None
        if not all(payload[key] for key in ("sub", "sid", "email", "role")) or payload["role"] == "Demo":
            return None
        return payload
    except (ValueError, TypeError, KeyError, UnicodeError):
        return None
