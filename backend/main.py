import importlib
import os
import pkgutil

from fastapi import FastAPI

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

# load all routers
include_all_routers(app, "backend")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("API_main:app", host="0.0.0.0", port=port, reload=True)
