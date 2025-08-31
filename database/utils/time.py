from database.WarframeDB import WarframeDB
from database.db_router import select


def get_last_update() -> int:
    rows = select("SELECT time FROM last_update")
    return rows[0][0] if rows else 0


def update_time(timestamp: int) -> None:
    # Keep local write path via SQLite; API uses only reads from D1
    WarframeDB().execute_query(f"UPDATE last_update SET time = {timestamp}")
