from dataclasses import dataclass
from typing import Dict, Any, List

"""
Example JSON:
[{
    'Activation': {'$date': {'$numberLong': '1754355047619'}},
    'AttackerMissionInfo': {'faction': 'FC_GRINEER', 
                            'seed': 109417},
    'AttackerReward': {'countedItems': [{'ItemCount': 1,
                                         'ItemType': '/Lotus/Types/Recipes/Weapons/DeraVandalBlueprint'}]},
    'ChainID': {'$oid': '68874b4e7524f2fbb3c59f36'},
    'Completed': True,
    'Count': -32037,
    'DefenderFaction': 'FC_GRINEER',
    'DefenderMissionInfo': {'faction': 'FC_CORPUS', 
                                       'seed': 906901},
    'DefenderReward': {'countedItems': [{'ItemCount': 1,
                                         'ItemType': '/Lotus/Types/Recipes/Weapons/WeaponParts/LatronWraithStock'}]},
    'Faction': 'FC_CORPUS',
    'Goal': 32000,
    'LocTag': '/Lotus/Language/Menu/CorpusInvasionGeneric',
    'Node': 'SolNode187',
    '_id': {'$oid': '689152e23ec2a27339c59f37'}
}]
"""


@dataclass
class RewardItem:
    item_count: int
    item_type: str

    @classmethod
    def parse_reward_item(cls, item_json: Dict[str, Any]) -> 'RewardItem':
        return cls(
            item_count=item_json.get('ItemCount', 0),
            item_type=item_json.get('ItemType', '')
        )


@dataclass
class InvasionReward:
    counted_items: List[RewardItem]

    @classmethod
    def parse_invasion_reward(cls, reward_json: Dict[str, Any]) -> 'InvasionReward':
        if not reward_json or isinstance(reward_json, list):
            return cls(counted_items=[])

        items = [RewardItem.parse_reward_item(item) for item in reward_json.get('countedItems', [])]
        return cls(counted_items=items)


@dataclass
class MissionInfo:
    faction: str
    seed: int

    @classmethod
    def parse_mission_info(cls, mission_json: Dict[str, Any]) -> 'MissionInfo':
        return cls(
            faction=mission_json.get('faction', ''),
            seed=mission_json.get('seed', 0)
        )


@dataclass
class Invasion:
    activation: int
    attacker_mission_info: MissionInfo
    attacker_reward: InvasionReward
    chain_id: str
    completed: bool
    count: int
    defender_faction: str
    defender_mission_info: MissionInfo
    defender_reward: InvasionReward
    faction: str
    goal: int
    loc_tag: str
    node: str
    _id: str

    @classmethod
    def parse_invasion(cls, invasion_json: Dict[str, Any]) -> 'Invasion':
        return cls(
            activation=int(invasion_json['Activation']['$date']['$numberLong']),
            attacker_mission_info=MissionInfo.parse_mission_info(invasion_json.get('AttackerMissionInfo', {})),
            attacker_reward=InvasionReward.parse_invasion_reward(invasion_json.get('AttackerReward', {})),
            chain_id=invasion_json.get('ChainID', {}).get('$oid', ''),
            completed=invasion_json.get('Completed', False),
            count=invasion_json.get('Count', 0),
            defender_faction=invasion_json.get('DefenderFaction', ''),
            defender_mission_info=MissionInfo.parse_mission_info(invasion_json.get('DefenderMissionInfo', {})),
            defender_reward=InvasionReward.parse_invasion_reward(invasion_json.get('DefenderReward', {})),
            faction=invasion_json.get('Faction', ''),
            goal=invasion_json.get('Goal', 0),
            loc_tag=invasion_json.get('LocTag', ''),
            node=invasion_json.get('Node', ''),
            _id=invasion_json.get('_id', {}).get('$oid', '')
        )
