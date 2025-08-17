from typing import Optional, List

import dotenv

dotenv.load_dotenv()

from database.WarframeDB import WarframeDB


def fetchall(query: str, params: Optional[tuple] = None) -> List[tuple]:
    db = WarframeDB()
    cur = db.cursor
    try:
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        rows = cur.fetchall()
    finally:
        db.conn.close()
    return rows
