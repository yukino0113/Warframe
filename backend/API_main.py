import os
from fastapi import FastAPI
import utils.logger  # noqa: F401 - initialize logging formatting

app = FastAPI(title="Warframe Drop API", version="v1")

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=False)
