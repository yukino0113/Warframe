import importlib
import os
import pkgutil

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
