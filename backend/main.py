import importlib
import os
import pkgutil
import time
from collections import deque, defaultdict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

import utils.logger  # noqa: F401 - initialize logging formatting

frontend_path = "../index.html"


def include_all_routers(app: FastAPI, base_package: str, base_prefix: str = ""):
    """Automatically include all routers in a package."""
    package = importlib.import_module(base_package)
    for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
        full_module_name = f"{base_package}.{module_name}"

        # If the module is a package, recursively include its routers
        if is_pkg:
            include_all_routers(app, full_module_name, f"{base_prefix}/{module_name}")
        else:
            module = importlib.import_module(full_module_name)
            if hasattr(module, "router"):
                app.include_router(
                    getattr(module, "router"), prefix=f"{base_prefix}/{module_name}"
                )


app = FastAPI(title="Warframe Drop API", version="v1")


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 90, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window_seconds
        self.hits = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        # Identify client by IP (use X-Forwarded-For when behind Caddy)
        xff = request.headers.get("x-forwarded-for")
        if xff:
            client_id = xff.split(",")[0].strip()
        else:
            client_id = request.client.host if request.client else "unknown"

        now = time.time()
        q = self.hits[client_id]
        # Remove timestamps older than window
        while q and now - q[0] >= self.window:
            q.popleft()
        if len(q) >= self.max_requests:
            # Too many requests
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Max 90 requests per 60 seconds.",
                },
                headers={
                    "Retry-After": str(int(self.window - (now - q[0]))),
                },
            )
        q.append(now)
        response = await call_next(request)
        return response


# Add rate limiting middleware
app.add_middleware(
    RateLimiterMiddleware,
    max_requests=90,
    window_seconds=60,
)

# CORS configuration: allow GitHub Pages frontend and local development
_default_origins = [
    "https://yukino0113.github.io",
    "https://yukino0113.github.io/",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
_env_origins = os.getenv("CORS_ORIGINS")
allow_origins = (
    [o.strip() for o in _env_origins.split(",") if o.strip()]
    if _env_origins
    else _default_origins
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# load all routers
include_all_routers(app, "backend")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("API_main:app", host="0.0.0.0", port=port, reload=True)
