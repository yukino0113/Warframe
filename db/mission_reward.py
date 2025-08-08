from typing import List

from db.utils.WarframeDB import WarframeDB, batch_insert_objects
from drop.utils.itemClass import MissionReward


def update_mission_rewards(mission_rewards: List[MissionReward]) -> bool:
    return batch_insert_objects(
        objects=mission_rewards,
        table_name='mission_rewards',
        columns=['price', 'rotation', 'rarity', 'drop_rate', 'source'],
        value_extractor=lambda reward: (reward.price, reward.rotation, reward.rarity, reward.drop_rate,
                                        reward.source)
    )


def create_mission_reward_table() -> None:
    WarframeDB().create_table('mission_rewards',
                              [
                                  'id INTEGER PRIMARY KEY AUTOINCREMENT',
                                  'price TEXT NOT NULL',
                                  'rotation TEXT NOT NULL',
                                  'rarity TEXT NOT NULL',
                                  'drop_rate DECIMAL(5,4) NOT NULL',
                                  'source TEXT NOT NULL',
                                  'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
                              ])


def delete_mission_reward_table() -> None:
    WarframeDB().drop_table('mission_rewards')
