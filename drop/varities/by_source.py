from dataclasses import dataclass
from typing import List, Tuple

from bs4.element import Tag

from drop.parser.commonParser import parse_three_cell_price, strip_text
from drop.utils.commonFunctions import is_empty_row
from .base_updater import BaseUpdater


@dataclass
class BySourceReward:
    source: str
    item: str
    rarity: str
    drop_rate: float


class GenericBySourceUpdater(BaseUpdater):
    table_name: str = ''

    def get_table_name(self) -> str:
        return self.table_name

    def get_table_schema(self) -> List[str]:
        return [
            'id INTEGER PRIMARY KEY AUTOINCREMENT',
            'item TEXT NOT NULL',
            'rarity TEXT NOT NULL',
            'drop_rate DECIMAL(5,4) NOT NULL',
            'source TEXT NOT NULL',
            'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        ]

    def get_columns(self) -> List[str]:
        return ['item', 'rarity', 'drop_rate', 'source']

    def extract_values(self, reward: BySourceReward) -> Tuple:
        return reward.item, reward.rarity, reward.drop_rate, reward.source

    def _parse_data(self) -> List[BySourceReward]:
        items: List[BySourceReward] = []
        current_source = ''

        def handle_header_row(th_row: Tag):
            nonlocal current_source
            ths = th_row.find_all('th')
            if not ths:
                return
            # first th is the source name; second th (if present) is "<Type> Drop Chance: X%" which we ignore
            current_source = strip_text(ths[0])

        for row in self.tables.find_all('tr'):
            if row.find('th'):
                handle_header_row(row)
            elif not is_empty_row(row):
                item, rarity, drop_rate = parse_three_cell_price(row.find('td'))
                items.append(BySourceReward(
                    source=current_source,
                    item=item,
                    rarity=rarity,
                    drop_rate=drop_rate
                ))
        return items


class UpdateModBySource(GenericBySourceUpdater):
    table_name = 'mod_drops_by_source'


class UpdateBlueprintBySource(GenericBySourceUpdater):
    table_name = 'blueprint_drops_by_source'


class UpdateResourceBySource(GenericBySourceUpdater):
    table_name = 'resource_drops_by_source'


class UpdateSigilBySource(GenericBySourceUpdater):
    table_name = 'sigil_drops_by_source'


class UpdateAdditionalItemBySource(GenericBySourceUpdater):
    table_name = 'additional_item_drops_by_source'


class UpdateRelicBySource(GenericBySourceUpdater):
    table_name = 'relic_drops_by_source'
