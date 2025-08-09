from dataclasses import dataclass
from typing import List, Tuple

from parser.drop_table.utils.commonParser import parse_two_cell_price, strip_text
from parser.drop_table.utils.commonFunctions import is_empty_row
from .base_updater import BaseUpdater


@dataclass
class KeyReward:
    source: str
    rotation: str
    price: str
    rarity: str
    drop_rate: float


class UpdateKeyReward(BaseUpdater):

    def get_table_name(self) -> str:
        return 'key_rewards'

    def get_table_schema(self) -> List[str]:
        return [
            'id INTEGER PRIMARY KEY AUTOINCREMENT',
            'price TEXT NOT NULL',
            'rotation TEXT NOT NULL',
            'rarity TEXT NOT NULL',
            'drop_rate DECIMAL(5,4) NOT NULL',
            'source TEXT NOT NULL',
            'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        ]

    def get_columns(self) -> List[str]:
        return ['price', 'rotation', 'rarity', 'drop_rate', 'source']

    def extract_values(self, reward: KeyReward) -> Tuple:
        return reward.price, reward.rotation, reward.rarity, reward.drop_rate, reward.source

    def _parse_data(self) -> List[KeyReward]:
        items: List[KeyReward] = []
        source = rotation = ""

        for row in self.tables.find_all('tr'):
            if title := row.find('th'):
                text = strip_text(title)
                if 'Rotation' in text:
                    rotation = text
                else:
                    source = text
            elif not is_empty_row(row):
                price, rarity, drop_rate = parse_two_cell_price(row.find('td'))
                items.append(KeyReward(
                    source=source,
                    rotation=rotation,
                    price=price,
                    rarity=rarity,
                    drop_rate=drop_rate
                ))
        return items
