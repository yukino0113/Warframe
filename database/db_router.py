import logging
import os
from typing import Any, List, Optional

import dotenv

dotenv.load_dotenv()

from database.clients.sqlite_client import SqliteClient
from database.clients.d1_client import D1Client


logger = logging.getLogger(__name__)


def _backend() -> str:
    # Default to D1; allow forcing sqlite by setting DB_BACKEND=sqlite
    return (os.getenv("DB_BACKEND") or "d1").lower()


def _sqlite_client() -> SqliteClient:
    return SqliteClient()


def _d1_client() -> D1Client:
    return D1Client()


# Read-only with automatic fallback


def select(query: str, params: Optional[List[Any]] = None) -> List[tuple]:
    # Normalize params for D1 compatibility
    if params is not None and not isinstance(params, (list, tuple)):
        params = [params]

    backend = _backend()

    # If user forces sqlite, don't attempt D1
    if backend == "sqlite":
        client = _sqlite_client()
        return client.select(query, list(params) if params is not None else None)

    # Try D1 first, then fall back to sqlite on failure (rate limit, network, config)
    try:
        d1 = _d1_client()
        return d1.select(query, list(params) if params is not None else None)
    except Exception as e:
        logger.warning("D1 select failed; falling back to SQLite. Reason: %s", e)
        try:
            sqlite = _sqlite_client()
            return sqlite.select(query, list(params) if params is not None else None)
        except Exception as e2:
            # Surface the original error context and the fallback error
            raise RuntimeError(
                f"Both D1 and SQLite selects failed. D1 error: {e}; SQLite error: {e2}"
            )
