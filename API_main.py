import os
from fastapi import FastAPI
import utils.logger  # noqa: F401 - initialize logging formatting

app = FastAPI(title="Warframe Drop API", version="v1")

from backend.item.search_item_source import *  # noqa: F401
from backend.relic.search_relic_source import *  # noqa: F401
from backend.prime.status import *  # noqa: F401



if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("API_main:app", host="0.0.0.0", port=port, reload=True)
