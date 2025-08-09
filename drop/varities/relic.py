from dataclasses import dataclass
from typing import List, Tuple

from drop.parser.commonParser import parse_two_cell_price, strip_text
from drop.utils.commonFunctions import is_empty_row
from .base_updater import BaseUpdater


@dataclass
class RelicReward:
    relic: str
    radiant: str
    price: str
    rarity: str
    drop_rate: float


class UpdateRelicReward(BaseUpdater):
    """聖物獎勵更新器"""

    def get_table_name(self) -> str:
        return 'relic_rewards'

    def get_table_schema(self) -> List[str]:
        return [
            'id INTEGER PRIMARY KEY AUTOINCREMENT',
            'price TEXT NOT NULL',
            'radiant TEXT NOT NULL',
            'rarity TEXT NOT NULL',
            'drop_rate DECIMAL(5,4) NOT NULL',
            'relic TEXT NOT NULL',
            'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        ]

    def get_columns(self) -> List[str]:
        return ['price', 'radiant', 'rarity', 'drop_rate', 'relic']

    def extract_values(self, reward: RelicReward) -> Tuple:
        return reward.price, reward.radiant, reward.rarity, reward.drop_rate, reward.relic

    def _parse_data(self) -> List[RelicReward]:
        """解析聖物獎勵資料"""
        items = []
        radiant = relic = ""

        for row in self.tables.find_all('tr'):
            if title := row.find('th'):
                text = strip_text(title)
                relic, radiant = ' '.join(text.split(' ')[:-1]), text.split(' ')[-1].strip('()')

            elif not is_empty_row(row):
                price, rarity, drop_rate = parse_two_cell_price(row.find('td'))
                items.append(RelicReward(
                    price=price,
                    rarity=rarity,
                    drop_rate=drop_rate,
                    relic=relic,
                    radiant=radiant
                ))
        return items
