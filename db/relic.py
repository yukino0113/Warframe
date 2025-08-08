from typing import List

from db.utils.WarframeDB import WarframeDB, batch_insert_objects
from drop.utils.itemClass import RelicReward


def update_relic_rewards(relic_rewards: List[RelicReward]) -> bool:
    return batch_insert_objects(
        objects=relic_rewards,
        table_name='relic_rewards',
        columns=['price', 'radiant', 'rarity', 'drop_rate', 'relic'],
        value_extractor=lambda reward: (reward.price, reward.radiant, reward.rarity,
                                        reward.drop_rate, reward.relic)
    )


def create_relic_reward_table() -> None:
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


def delete_relic_reward_table() -> None:
    WarframeDB().drop_table('relic_rewards')
