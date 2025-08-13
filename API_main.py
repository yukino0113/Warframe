import importlib
import os
import pkgutil

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import utils.logger  # noqa: F401 - initialize logging formatting

app = FastAPI(title="Warframe Drop API", version="v1")

frontend_path = "frontend/index.html"

# Mount static frontend at /ui
app.mount("/ui", StaticFiles(directory="frontend", html=True), name="ui")


def include_all_routers(app: FastAPI, base_package: str, base_prefix: str = ""):
    """Automatically include all routers in a package."""
    try:
        package = importlib.import_module(base_package)
    except Exception:
        return
    pkg_path = getattr(package, "__path__", None)
    if not pkg_path:
        return
    for _, module_name, is_pkg in pkgutil.iter_modules(pkg_path):
        full_module_name = f"{base_package}.{module_name}"
        prefix = f"{base_prefix}/{module_name}".replace("//", "/")
        if is_pkg:
            include_all_routers(app, full_module_name, prefix)
        else:
            try:
                module = importlib.import_module(full_module_name)
            except Exception:
                continue
            router = getattr(module, "router", None)
            if router is not None:
                app.include_router(router, prefix=prefix)


# load all routers
include_all_routers(app, "backend")


# SPA fallback routes: serve frontend for root and any non-API path
@app.get("/")
async def index():
    return FileResponse(frontend_path)


@app.get("/{path:path}")
async def spa_catch_all(path: str, request: Request):
    # Let API and /ui static mount handle their routes; return index.html otherwise
    if path.startswith("v1/") or path.startswith("ui/"):
        return FileResponse(frontend_path)
    return FileResponse(frontend_path)



if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("API_main:app", host="0.0.0.0", port=port, reload=True)
