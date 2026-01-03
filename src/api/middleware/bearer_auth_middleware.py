from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ...core.config import app_config


class BearerAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, excluded_paths: tuple[str] | None = None) -> None:
        super().__init__(app)
        self._excluded_paths = excluded_paths or (
            "/docs",
            "/redoc",
            "/openapi.json",
        )

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self._excluded_paths:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authorization header missing"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid authentication scheme"},
                    headers={"WWW-Authenticate": "Bearer"},
                )

        except ValueError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid Authorization header format"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        expected_token = app_config.SERVER.TOKEN.get_secret_value()
        if not expected_token:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Server configuration error: AUTH_TOKEN not set"},
            )

        if token != expected_token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Incorrect Bearer Token"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        return await call_next(request)
