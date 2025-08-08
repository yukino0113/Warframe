from dataclasses import dataclass
from typing import List, Tuple

from bs4.element import Tag

from drop.parser.commonParser import strip_text, parse_row_source_chance
from drop.utils.commonFunctions import is_empty_row
from .base_updater import BaseUpdater


@dataclass
class ByItemReward:
    item: str  # Mod or Blueprint/Item name (section header)
    source: str
    rarity: str
    drop_rate: float


class GenericByItemUpdater(BaseUpdater):
    table_name: str = ''

    def get_table_name(self) -> str:
        return self.table_name

    def get_table_schema(self) -> List[str]:
        return [
            'id INTEGER PRIMARY KEY AUTOINCREMENT',
            'item TEXT NOT NULL',
            'source TEXT NOT NULL',
            'rarity TEXT NOT NULL',
            'drop_rate DECIMAL(5,4) NOT NULL',
            'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        ]

    def get_columns(self) -> List[str]:
        return ['item', 'source', 'rarity', 'drop_rate']

    def extract_values(self, reward: ByItemReward) -> Tuple:
        return reward.item, reward.source, reward.rarity, reward.drop_rate

    def _parse_data(self) -> List[ByItemReward]:
        items: List[ByItemReward] = []
        current_item = ''

        def handle_header_row(th_row: Tag):
            nonlocal current_item
            ths = th_row.find_all('th')
            if not ths:
                return
            # For item sections, headers appear as <th colspan="3">Item Name</th>
            # or a column-name header row which we ignore (contains 'Source')
            header_text = strip_text(ths[0])
            if 'Source' in header_text:
                return
            current_item = header_text

        for row in self.tables.find_all('tr'):
            if row.find('th'):
                handle_header_row(row)
            elif not is_empty_row(row):
                # Row structure: [source] [drop chance] [rarity%]
                source, rarity, drop_rate = parse_row_source_chance(row.find('td'))
                items.append(ByItemReward(
                    item=current_item,
                    source=source,
                    rarity=rarity,
                    drop_rate=drop_rate
                ))
        return items


class UpdateModByMod(GenericByItemUpdater):
    table_name = 'mod_drops_by_mod'


class UpdateBlueprintByItem(GenericByItemUpdater):
    table_name = 'blueprint_drops_by_item'


class UpdateResourceByResource(GenericByItemUpdater):
    table_name = 'resource_drops_by_resource'
