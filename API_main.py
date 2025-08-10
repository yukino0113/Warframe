import os
from fastapi import FastAPI
import utils.logger  # noqa: F401 - initialize logging formatting

app = FastAPI(title="Warframe Drop API", version="v1")

from backend.item_drop_search.search_item_source import *
from backend.relic_drop_search.search_relic_source import *


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("API_main:app", host="0.0.0.0", port=port, reload=True)
