"""Drop-in WSGI shared-cookie authentication for trusted VTAB satellite apps."""
import json
import os
import urllib.error
import urllib.parse
import urllib.request

from vtab_identity import IDENTITY_COOKIE, read_cookie, require_secret, verify_vtab_token


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class VtabAuthenticator:
    def __init__(self, secret=None, verify_url="http://127.0.0.1:8003/api/auth/verify", online=True):
        self.secret = secret if secret is not None else os.environ.get("VTAB_SECRET_KEY", "").encode()
        require_secret(self.secret)
        self.online = online
        self.verify_url = verify_url
        parsed = urllib.parse.urlsplit(verify_url)
        if (parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password
                or parsed.query or parsed.fragment or parsed.path != "/api/auth/verify"
                or (parsed.scheme == "http" and parsed.hostname not in ("127.0.0.1", "::1", "localhost"))):
            raise ValueError("Use a loopback HTTP or trusted HTTPS /api/auth/verify endpoint")
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirect())

    def authenticate(self, cookie_header):
        token = read_cookie(cookie_header, IDENTITY_COOKIE)
        identity = verify_vtab_token(token, self.secret)
        if not identity:
            return None
        if not self.online:
            return identity
        request = urllib.request.Request(self.verify_url, headers={"Authorization": "Bearer " + token, "Accept": "application/json"})
        try:
            with self.opener.open(request, timeout=3) as response:
                result = json.loads(response.read(16385))
            current = result.get("identity") if result.get("authenticated") is True else None
            if (not isinstance(current, dict) or current.get("sub") != identity["sub"]
                    or any(not isinstance(current.get(key), str) for key in ("email", "name", "role", "employee_id"))):
                return None
            # Authoritative fields ensure changed roles are applied immediately.
            identity.update(current)
            return identity
        except urllib.error.HTTPError as error:
            error.close()
            return None
        except (OSError, ValueError, urllib.error.URLError, AttributeError, TypeError):
            return None


class VtabSSOMiddleware:
    """Protect all routes except exact public paths. Does not create another session."""
    def __init__(self, app, *, public_paths=("/health",), **options):
        self.app = app
        self.auth = VtabAuthenticator(**options)
        self.public_paths = frozenset(public_paths)

    def __call__(self, environ, start_response):
        if environ.get("PATH_INFO", "/") in self.public_paths:
            return self.app(environ, start_response)
        identity = self.auth.authenticate(environ.get("HTTP_COOKIE", ""))
        if not identity:
            body = b'{"error":"authentication_required"}'
            start_response("401 Unauthorized", [("Content-Type", "application/json"),
                           ("Cache-Control", "no-store"), ("Content-Length", str(len(body)))])
            return [body]
        environ["vtab.identity"] = identity
        environ["REMOTE_USER"] = identity["email"]
        return self.app(environ, start_response)
