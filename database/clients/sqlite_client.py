import os
import sqlite3
from typing import Any, List, Optional


class SqliteClient:
    def __init__(self, db_name: Optional[str] = None):
        env_db_name = os.getenv("DB_NAME") or os.getenv("DB_PATH") or "data/warframe.db"
        self.conn = sqlite3.connect(db_name or env_db_name)
        self.cur = self.conn.cursor()

    def select(self, query: str, params: Optional[List[Any]] = None) -> List[tuple]:
        try:
            if params:
                self.cur.execute(query, params)
            else:
                self.cur.execute(query)
            return self.cur.fetchall()
        finally:
            self.conn.close()
