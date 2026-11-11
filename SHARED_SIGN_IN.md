# VTAB shared sign-in deployment

## Included changes

The portal issues `vtab_session` and an HS256 JWT `vtab_identity` after a successful
email OTP sign-in or OTP password recovery. Both expire after at most 12 hours.
Production hosts matching `vtabsquare.com` or a real subdomain receive
`Domain=.vtabsquare.com; Path=/; HttpOnly; Secure; SameSite=Lax`. Localhost receives
host-only cookies. Lookalike domain names never enable parent-domain cookies.
Password hashing and existing session signatures/database schema are unchanged.

Demo and unverified self-registration sessions remain host-only and never receive
a federated identity. An existing portal login remains valid; sign out and complete
email OTP sign-in once to obtain the new shared cookies. New login and logout clear
legacy host-only and parent-domain cookies before setting replacements. Password
recovery also revokes the user's older sessions.

`GET /api/auth/verify` accepts `Authorization: Bearer <identity-token>` or the
identity cookie. It validates signature, algorithm, issuer, audience, purpose,
timestamps, active user and unexpired database session. Responses are JSON with
`Cache-Control: no-store`: 200 authenticated, 401 invalid/revoked, 503 unavailable.
Current profile and role fields come from the database. No password hash or CSRF
token is returned. There is no permissive CORS configuration.

## Portal deployment

1. Back up the deployed source and service environment. Deploy this directory's
   source and public assets. No database migration is required.
2. Keep the existing `DATABASE_URL`, Brevo/email configuration and legacy
   `VTAB_SSO_SECRET` in the service's protected environment, not in source files.
3. Set `VTAB_SECRET_KEY` to a cryptographically random secret of at least 32 bytes,
   identically on the portal and trusted satellite servers. If your current key is
   already strong, keep it to preserve existing sessions. Rotating it invalidates
   signed sessions and identity tokens. Generate a new key when needed with:

   ```sh
   python -c 'import secrets; print(secrets.token_urlsafe(48))'
   ```

4. Set `VTAB_ENV=production`, `VTAB_HOST=127.0.0.1`, `VTAB_PORT=8003`. If `PORT`
   is set, it takes precedence over `VTAB_PORT`; ensure it is also 8003 or unset.
   Run behind the existing HTTPS reverse proxy. The proxy must preserve the real
   public `Host` (`proxy_set_header Host $host;`) and redirect HTTP to HTTPS.
   Production cookie issuance rejects missing/development/short signing keys.
5. Keep port 8003 private. For satellites on this droplet use the loopback endpoint.
   In the public portal Nginx server block, prevent external verification access:

   ```nginx
   location = /api/auth/verify { return 404; }
   ```

   Satellites on another server need a separately protected HTTPS verification
   route with network access controls; configure `verify_url` accordingly. Never
   forward bearer tokens to plaintext public IP URLs or log Authorization/Cookie.
6. Restart the service. In Admin applications, configure the actual Marketing and
   Sales entries with `shared_session` and their HTTPS subdomain URLs. Existing
   application records and legacy assertion integrations are retained; no records
   are silently rewritten or duplicated. Shared-cookie launch uses the ordinary
   application URL without putting a token in the address bar.

The supplied startup file and runbook contained embedded credentials. These have
been replaced with environment-based configuration/placeholders. Rotate the
previously embedded database, email API and legacy SSO credentials before release;
removing them from this package does not revoke old copies. Git history, cached
bytecode, the old app backup and local database are omitted from the delivery ZIP.

## Satellite integration (required for zero-login access)

The provided ZIP contained only VTAB 360, not Marketing or Sales source code. Copy
`vtab_identity.py` and `vtab_sso_middleware.py` into each satellite and configure
the shared `VTAB_SECRET_KEY` in that server's environment. The middleware uses
only Python's standard library and requires no database credentials.

For Flask or another WSGI application:

```python
from vtab_sso_middleware import VtabSSOMiddleware

app.wsgi_app = VtabSSOMiddleware(
    app.wsgi_app,
    verify_url="http://127.0.0.1:8003/api/auth/verify",
    public_paths=("/health",),
)
```

For a plain WSGI callable, use `application = VtabSSOMiddleware(application)`.
The authenticated identity is in `environ["vtab.identity"]`; the email is also
in `environ["REMOTE_USER"]`. In Flask, read `request.environ["vtab.identity"]`.
Update the satellite's existing login guard to accept this verified identity and
load/map its own application account. Otherwise its old guard will still show
a login screen. Authentication does not grant every user administrator access:
enforce the satellite's own account permissions and role checks on every route.
Keep its existing CSRF protection for state-changing requests. Do not copy the
identity into a long-lived local session that bypasses subsequent validation.

For non-WSGI frameworks, call `VtabAuthenticator().authenticate(cookie_header)`
in their request hook; reject `None`, otherwise attach the returned identity to
the framework's user context. The supplied adapter does not automatically modify
ASGI/Django authentication backends or any unavailable satellite source files.

Online validation is enabled by default on every protected request, with a
three-second timeout, no redirects and no environment HTTP proxy forwarding.
An outage denies access. This ensures revoked sessions, inactive users and role
changes take effect on the next protected request, without a revocation cache.
Verification uses Supabase, so latency depends on the network/database; no <2ms
performance guarantee is made.

`online=False` enables local signature-only verification. Use it only if you
accept that a stolen token, logout or account change may not be recognized until
token expiry (up to 12 hours). It is not the default.

## Trust boundary

All applications receiving parent-domain cookies must be trusted. HttpOnly stops
browser JavaScript from reading a cookie; each receiving server can still see it.
With HS256, every holder of the shared key can also mint tokens. Do not share the
key with external applications or put it in frontend code. The identity token is
signed, not encrypted. SameSite=Lax is only partial CSRF protection, especially
between sibling subdomains; it does not replace CSRF tokens or origin checks.
References: [MDN Set-Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie),
[MDN cookie security](https://developer.mozilla.org/en-US/docs/Web/Security/Practical_implementation_guides/Cookies).

## Verification performed

Run `python -m unittest test_shared_sso -v` and
`python -m py_compile app.py vtab_identity.py vtab_sso_middleware.py start_server.py`.
The 12 tests cover signed claims, tampering, expiry, cookie domains, duplicates,
weak keys, demo/registration isolation, legacy session compatibility, migration
cookie deletion, local development, WSGI authentication, database failure and a
real loopback HTTP verification/logout flow including role changes/deactivation.
Tests use an in-memory database double and do not connect to Supabase or send OTPs.

Live deployment, actual Supabase/email delivery and browser navigation between
the three production subdomains still require verification in your environment.
After integrating both satellites, sign in once via OTP, open each app, confirm
identity/permissions, sign out of the portal and confirm protected satellite
requests are denied. Also verify localhost login and existing legacy SSO apps.
