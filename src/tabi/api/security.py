"""Ephemeral single-worker sessions; secrets never enter URLs, files or logs here."""

import hashlib
import os
import secrets
import threading
import time

from starlette.responses import JSONResponse

from .contracts import WebSession

SAFE_HEADERS = {
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Content-Security-Policy": (
        "default-src 'self'; script-src 'self'; style-src 'self'; "
        "img-src 'self' blob: data:; media-src 'self' blob:; connect-src 'self'; "
        "object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
    ),
}


class Sessions:
    def __init__(self, *, lifetime=12 * 60 * 60, bootstrap_lifetime=90):
        if type(lifetime) is not int or not 1 <= lifetime <= 86400:
            raise ValueError("session lifetime must be an integer from 1 to 86400 seconds")
        self.id = secrets.token_hex(16)
        self.cookie_name = f"tabi_{self.id}"
        self.cookie = secrets.token_urlsafe(32)
        self.bearer = secrets.token_urlsafe(32)
        self.csrf = secrets.token_urlsafe(32)
        self.lifetime, self.bootstrap_lifetime = lifetime, bootstrap_lifetime
        self.expires = time.monotonic() + lifetime
        self.tickets = {}
        self.lock = threading.Lock()

    def ticket(self):
        token = secrets.token_urlsafe(32)
        with self.lock:
            now = time.monotonic()
            self.tickets = {key: expiry for key, expiry in self.tickets.items() if expiry > now}
            if len(self.tickets) >= 16:
                raise ValueError("too many unredeemed browser tickets")
            self.tickets[hashlib.sha256(token.encode()).digest()] = now + self.bootstrap_lifetime
        return token

    def exchange(self, token):
        with self.lock:
            expiry = self.tickets.pop(hashlib.sha256(token.encode()).digest(), 0)
            if expiry <= time.monotonic():
                return False
            self.expires = time.monotonic() + self.lifetime
            return True

    def valid_cookie(self, value):
        return (
            value is not None
            and time.monotonic() < self.expires
            and secrets.compare_digest(value, self.cookie)
        )

    def valid_bearer(self, value):
        return value is not None and secrets.compare_digest(value, f"Bearer {self.bearer}")

    def info(self, stopping):
        return WebSession(
            schema_version="1.0",
            session_id=self.id,
            pid=os.getpid(),
            csrf=self.csrf,
            expires_in=max(0, int(self.expires - time.monotonic())),
            stopping=stopping,
        )


class SecurityBoundary:
    """ASGI boundary applies before routing, including media, SSE and errors."""

    def __init__(self, app, *, sessions, origin):
        self.app, self.sessions, self.origin = app, sessions, origin
        self.host = origin.removeprefix("http://")

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        headers = {}
        duplicates = set()
        for key, value in scope["headers"]:
            name = key.decode("latin-1").lower()
            if name in headers:
                duplicates.add(name)
            headers[name] = value.decode("latin-1")

        async def guarded_send(message):
            if message["type"] == "http.response.start":
                existing = {name.lower() for name, _ in message["headers"]}
                message["headers"] += [
                    (key.lower().encode(), value.encode())
                    for key, value in SAFE_HEADERS.items()
                    if key.lower().encode() not in existing
                ]
            await send(message)

        async def reject(status, detail):
            await JSONResponse({"detail": detail}, status_code=status)(scope, receive, guarded_send)

        if (
            duplicates & {"host", "origin", "authorization", "cookie", "x-tabi-csrf"}
            or headers.get("host") != self.host
            or headers.get("origin") not in {None, self.origin}
            or (scope["path"].startswith("/api/") and headers.get("sec-fetch-site") == "cross-site")
        ):
            await reject(403, "Request origin is not this local workspace")
            return
        path = scope["path"]
        if "\\" in path or any(part in {".", ".."} for part in path.split("/")):
            await reject(400, "Invalid path")
            return
        if path.startswith("/api/"):
            bearer = self.sessions.valid_bearer(headers.get("authorization"))
            scope.setdefault("state", {})["bearer"] = bearer
            from starlette.requests import Request

            cookie = Request(scope).cookies.get(self.sessions.cookie_name)
            if path != "/api/v1/bootstrap" and not (bearer or self.sessions.valid_cookie(cookie)):
                await reject(401, "Session expired or missing; reopen from the local launcher")
                return
            if scope["method"] not in {"GET", "HEAD"} and not bearer:
                if headers.get("origin") != self.origin:
                    await reject(403, "Same-origin browser request required")
                    return
                if path != "/api/v1/bootstrap" and not secrets.compare_digest(
                    headers.get("x-tabi-csrf", ""), self.sessions.csrf
                ):
                    await reject(403, "Missing or invalid CSRF token")
                    return
            if scope["method"] not in {"GET", "HEAD"}:
                try:
                    size = int(headers.get("content-length", "-1"))
                except ValueError:
                    size = -1
                if not 0 <= size <= 16 * 1024 * 1024:
                    await reject(413, "JSON request needs a bounded Content-Length")
                    return
                if headers.get("content-type", "").split(";")[0] != "application/json":
                    await reject(415, "application/json required")
                    return
        await self.app(scope, receive, guarded_send)
