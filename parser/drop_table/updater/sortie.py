from dataclasses import dataclass
from typing import List, Tuple

from parser.drop_table.utils.commonParser import parse_two_cell_prize, strip_text
from parser.drop_table.utils.commonFunctions import is_empty_row
from .base_updater import BaseUpdater


@dataclass
class SortieReward:
    source: str
    prize: str
    rarity: str
    drop_rate: float


class UpdateSortieReward(BaseUpdater):

    def get_table_name(self) -> str:
        return 'sortie_rewards'

    def get_table_schema(self) -> List[str]:
        return [
            'id INTEGER PRIMARY KEY AUTOINCREMENT',
            'prize TEXT NOT NULL',
            'rarity TEXT NOT NULL',
            'drop_rate DECIMAL(5,4) NOT NULL',
            'source TEXT NOT NULL',
            'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        ]

    def get_columns(self) -> List[str]:
        return ['prize', 'rarity', 'drop_rate', 'source']

    def extract_values(self, reward: SortieReward) -> Tuple:
        return reward.prize, reward.rarity, reward.drop_rate, reward.source

    def _parse_data(self) -> List[SortieReward]:
        items: List[SortieReward] = []
        source = ""

        for row in self.tables.find_all('tr'):
            if title := row.find('th'):
                # The Sorties table has a single header like "Sortie"
                text = strip_text(title)
                source = text
            elif not is_empty_row(row):
                prize, rarity, drop_rate = parse_two_cell_prize(row.find('td'))
                items.append(SortieReward(
                    source=source,
                    prize=prize,
                    rarity=rarity,
                    drop_rate=drop_rate
                ))
        return items
