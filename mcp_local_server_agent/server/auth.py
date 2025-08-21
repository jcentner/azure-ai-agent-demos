# server/auth.py
from __future__ import annotations

from typing import Optional, Callable, Awaitable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from .errors import UnauthorizedError


def extract_bearer_token(header_value: Optional[str]) -> Optional[str]:
    if not header_value:
        return None
    prefix = "Bearer "
    return header_value[len(prefix):] if header_value.startswith(prefix) else None


class BearerAuthMiddleware(BaseHTTPMiddleware):
    """
    Starlette middleware that enforces Authorization: Bearer <token> for requests
    under the MCP mount path. If token is None, middleware is a no-op.
    """

    def __init__(self, app, *, token: Optional[str], mount_path: str):
        super().__init__(app)
        self._token = token
        self._mount_path = mount_path.rstrip("/") or "/"

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        if not self._token:
            return await call_next(request)

        path = request.url.path
        if path == self._mount_path or path.startswith(self._mount_path + "/"):
            token = extract_bearer_token(request.headers.get("Authorization"))
            if token != self._token:
                return JSONResponse({"error": "unauthorized"}, status_code=401)

        return await call_next(request)
