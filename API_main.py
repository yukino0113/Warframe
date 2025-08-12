import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import utils.logger  # noqa: F401 - initialize logging formatting

app = FastAPI(title="Warframe Drop API", version="v1")

# Mount static frontend at /ui
app.mount("/ui", StaticFiles(directory="frontend", html=True), name="ui")

from backend.item.source_item import *  # noqa: F401
from backend.relic.relic_source_item import *  # noqa: F401
from backend.prime.status import *  # noqa: F401


# SPA fallback routes: serve frontend for root and any non-API path
@app.get("/")
async def index():
    return FileResponse("frontend/index.html")


@app.get("/{path:path}")
async def spa_catch_all(path: str, request: Request):
    # Let API and /ui static mount handle their routes; return index.html otherwise
    if path.startswith("v1/") or path.startswith("ui/"):
        return FileResponse("frontend/index.html")
    return FileResponse("frontend/index.html")



if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("API_main:app", host="0.0.0.0", port=port, reload=True)
