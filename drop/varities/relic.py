from dataclasses import dataclass
from typing import List

from drop.db.WarframeDB import WarframeDB, batch_insert_objects
from drop.parser.commonParser import parse_two_cell_price
from drop.utils.commonFunctions import strip_text, is_empty_row
from bs4.element import Tag


@dataclass
class RelicReward:
    relic: str
    radiant: str
    price: str
    rarity: str
    drop_rate: float


class UpdateRelicReward:
    def __init__(self, tables: Tag):
        self.tables = tables

    def run_update(self) -> None:
        self._delete_relic_reward_table()
        self._create_relic_reward_table()
        self._update_relic_rewards(self._relic_parser())

    def _relic_parser(self):
        items = []
        radiant = relic = ""

        for row in self.tables.find_all('tr'):
            if title := row.find('th'):
                text = strip_text(title)
                relic, radiant = ' '.join(text.split(' ')[:-1]), text.split(' ')[-1].strip('()')

            elif not is_empty_row(row):
                price, rarity, drop_rate = parse_two_cell_price(row.find('td'))
                items.append(RelicReward(price=price, rarity=rarity,
                                         drop_rate=drop_rate, relic=relic, radiant=radiant))
        return items

    @staticmethod
    def _update_relic_rewards(relic_rewards: List[RelicReward]) -> bool:
        return batch_insert_objects(
            objects=relic_rewards,
            table_name='relic_rewards',
            columns=['price', 'radiant', 'rarity', 'drop_rate', 'relic'],
            value_extractor=lambda reward: (reward.price, reward.radiant, reward.rarity,
                                            reward.drop_rate, reward.relic)
        )

    @staticmethod
    def _create_relic_reward_table() -> None:
        WarframeDB().create_table('relic_rewards',
                                  [
                                      'id INTEGER PRIMARY KEY AUTOINCREMENT',
                                      'price TEXT NOT NULL',
                                      'radiant TEXT NOT NULL',
                                      'rarity TEXT NOT NULL',
                                      'drop_rate DECIMAL(5,4) NOT NULL',
                                      'relic TEXT NOT NULL',
                                      'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
                                  ])

    @staticmethod
    def _delete_relic_reward_table() -> None:
        WarframeDB().drop_table('relic_rewards')
