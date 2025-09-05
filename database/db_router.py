import logging
from typing import Any, List, Optional

import dotenv

from database.clients.sqlite_client import SqliteClient

dotenv.load_dotenv()

logger = logging.getLogger(__name__)


def _sqlite_client() -> SqliteClient:
    return SqliteClient()


# Read-only, SQLite only


def select(query: str, params: Optional[List[Any]] = None) -> List[tuple]:
    # Normalize params
    if params is not None and not isinstance(params, (list, tuple)):
        params = [params]

    client = _sqlite_client()
    return client.select(query, list(params) if params is not None else None)
