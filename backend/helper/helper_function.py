from typing import Optional, List, Any

import dotenv

dotenv.load_dotenv()

from database.db_router import select


def fetchall(query: str, params: Optional[Any] = None) -> List[tuple]:
    # Normalize params for D1 compatibility; keep signature stable
    if params is None:
        return select(query)
    if not isinstance(params, (list, tuple)):
        params = [params]
    return select(query, list(params))
