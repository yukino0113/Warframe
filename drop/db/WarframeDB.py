from typing import Any, List
import logging
import sqlite3
import os
import dotenv

dotenv.load_dotenv()


def batch_insert_objects(objects: List[Any], table_name: str, columns: List[str],
                         value_extractor, chunk_size: int = 5000) -> bool:
    if not objects:
        return False

    placeholders = ', '.join(['?' for _ in columns])
    insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

    try:
        total_inserted = 0
        logging.debug(f'DB Action: START BATCH INSERT {len(objects)} items to {table_name}')

        for i in range(0, len(objects), chunk_size):
            chunk = objects[i:i + chunk_size]
            values = [value_extractor(obj) for obj in chunk]

            logging.debug(
                f'DB Action: INSERTING ITEMS to {table_name}, ({chunk_size} of remaining {len(objects) - total_inserted} items)')
            WarframeDB().execute_many(insert_sql, values)
            total_inserted += len(chunk)
            logging.info(
                f"DB Action: BATCH ITEMS INSERTED to {table_name}, current progress: {total_inserted}/{len(objects)}")

        logging.info(f"DB Action: BATCH ITEMS INSERTED COMPLETE, total items: {total_inserted}/{len(objects)}")
        return True

    except Exception as e:
        logging.error(f"DB Action: BATCH INSERT FAILED, ERROR: {e}")
        return False


class WarframeDB:
    def __init__(self, db_name=None):
        # Prefer DB_NAME, then DB_PATH, then default file path
        env_db_name = os.getenv('DB_NAME') or os.getenv('DB_PATH') or 'drop/db/warframe.db'
        self.conn = sqlite3.connect(db_name or env_db_name)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name: str, columns: List[str]) -> None:
        try:
            logging.debug(f'DB action: CREATE TABLE IF NOT EXISTS {table_name} ({", ".join(columns)})')
            self.cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name} ({", ".join(columns)})')
        except Exception as e:
            logging.error(f'DB action: CREATE TABLE IF NOT EXISTS {table_name} ({", ".join(columns)}), ERROR: {e}')
        self.conn.close()

    def drop_table(self, table_name: str) -> None:
        try:
            logging.debug(f'DB action: DROP TABLE IF EXISTS {table_name}')
            self.cursor.execute(f'DROP TABLE IF EXISTS {table_name}')
        except Exception as e:
            logging.error(f'DB action: DROP TABLE IF EXISTS {table_name}, ERROR: {e}')
        self.conn.close()

    def execute_query(self, query: str) -> None:
        try:
            self.cursor.execute(query)
            logging.debug(f'DB action: {query}')
            self.conn.commit()
        except Exception as e:
            logging.error(f'DB action: {query}, ERROR: {e}')
        self.conn.close()

    def execute_many(self, query: str, values: List[tuple]) -> None:
        try:
            self.cursor.executemany(query, values)
            self.conn.commit()
        except Exception as e:
            logging.error(f'DB action: EXECUTE_MANY, ERROR: {e}')
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
