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


def include_all_routers(app: FastAPI, package_name: str, prefix: str = ""):
    package = importlib.import_module(package_name)
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{package_name}.{module_name}")
        if hasattr(module, "router"):
            app.include_router(getattr(module, "router"), prefix=f"{prefix}/{module_name}")


# 建立 FastAPI app
app = FastAPI()

# 載入所有 routers
include_all_routers(app, "backend.item", prefix="/item")
include_all_routers(app, "backend.relic", prefix="/relic")
include_all_routers(app, "backend.prime", prefix="/prime")


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
