from abc import ABC, abstractmethod
from typing import List, Any, Tuple
import logging
from bs4.element import Tag

from drop.db.WarframeDB import WarframeDB, batch_insert_objects


class BaseUpdater(ABC):

    def __init__(self, tables: Tag):
        self.tables = tables

    def run_update(self) -> None:
        logging.info(f"MainUpdate: Start updating {self.get_table_name()} ")
        self._delete_table()
        self._create_table()
        items = self._parse_data()
        self._update_data(items)

    @abstractmethod
    def _parse_data(self) -> List[Any]:
        pass

    @abstractmethod
    def get_table_name(self) -> str:
        pass

    @abstractmethod
    def get_table_schema(self) -> List[str]:
        pass

    @abstractmethod
    def get_columns(self) -> List[str]:
        pass

    @abstractmethod
    def extract_values(self, item: Any) -> Tuple:
        pass

    def _delete_table(self) -> None:
        WarframeDB().drop_table(self.get_table_name())

    def _create_table(self) -> None:
        WarframeDB().create_table(self.get_table_name(), self.get_table_schema())

    def _update_data(self, items: List[Any]) -> bool:
        return batch_insert_objects(
            objects=items,
            table_name=self.get_table_name(),
            columns=self.get_columns(),
            value_extractor=self.extract_values
        )
