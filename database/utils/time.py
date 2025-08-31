import logging

from database.WarframeDB import WarframeDB
from database.db_router import select


def get_last_update() -> int:
    """Return last update timestamp or 0 if table is missing/unavailable.

    Be defensive because remote D1 may be misconfigured in some envs; we don't
    want this to break read-only endpoints that can work without cache key.
    """
    try:
        rows = select("SELECT time FROM last_update")
        return int(rows[0][0]) if rows and rows[0] and rows[0][0] is not None else 0
    except Exception:
        logging.warning("get_last_update failed; defaulting to 0", exc_info=True)
        return 0


def update_time(timestamp: int) -> None:
    # Keep local write path via SQLite; API uses only reads from D1
    WarframeDB().execute_query(f"UPDATE last_update SET time = {timestamp}")
