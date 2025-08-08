from dataclasses import dataclass
from typing import List

from drop.db.WarframeDB import WarframeDB, batch_insert_objects
from drop.parser.commonParser import parse_two_cell_price
from drop.utils.commonFunctions import strip_text, is_empty_row


@dataclass
class MissionReward:
    source: str
    rotation: str
    price: str
    rarity: str
    drop_rate: float


def mission_parser(tables):
    items = []
    source = rotation = ""

    for row in tables.find_all('tr'):
        if title := row.find('th'):
            text = strip_text(title)
            rotation = text if 'Rotation' in text else rotation
            source = text if 'Rotation' not in text else source

        elif not is_empty_row(row):
            price, rarity, drop_rate = parse_two_cell_price(row.find('td'))
            items.append(MissionReward(source=source, rotation=rotation, price=price, rarity=rarity,
                                       drop_rate=drop_rate))
    return items


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
