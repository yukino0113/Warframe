from typing import Any
import logging
import sqlite3


class WarframeDB:
    def __init__(self, db_name='db/warframe.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()


    def execute_query(self, query: str) -> None:
        try:
            self.cursor.execute(query)
            logging.debug(f'DB action: {query}')
            self.conn.commit()
        except Exception as e:
            logging.error(f'DB action: {query}, ERROR: {e}')
        self.conn.close()

    def fetch_all(self, query: str) -> Any:
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            logging.debug(f'DB action: {query}, result: {result}')
        except Exception as e:
            logging.error(f'DB action: {query}, ERROR: {e}')
            result = None
        self.conn.close()
        return result