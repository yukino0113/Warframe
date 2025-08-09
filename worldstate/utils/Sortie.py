from dataclasses import dataclass
from typing import Dict, Any, List

"""
Example JSON:
[{'Activation': {'$date': {'$numberLong': '1754409600000'}},
                            'Boss': 'SORTIE_BOSS_VOR',
                            'Expiry': {'$date': {'$numberLong': '1754496000000'}},
                            'ExtraDrops': [],
                            'Reward': '/Lotus/Types/Game/MissionDecks/SortieRewards',
                            'Seed': 25131,
                            'Twitter': True,
                            'Variants': [{'missionType': 'MT_MOBILE_DEFENSE',
                                          'modifierType': 'SORTIE_MODIFIER_PUNCTURE',
                                          'node': 'SolNode119',
                                          'tileset': 'GrineerAsteroidTileset'},
                                         {'missionType': 'MT_RESCUE',
                                          'modifierType': 'SORTIE_MODIFIER_ELECTRICITY',
                                          'node': 'SolNode188',
                                          'tileset': 'GrineerGalleonTileset'},
                                         {'missionType': 'MT_DEFENSE',
                                          'modifierType': 'SORTIE_MODIFIER_EXIMUS',
                                          'node': 'SolNode745',
                                          'tileset': 'GrineerFortressTileset'}],
                            '_id': {'$oid': '689226ff390dd78e92c59f36'}}]"""


@dataclass
class SortieVariant:
    mission_type: str
    modifier_type: str
    node: str
    tileset: str

    @classmethod
    def from_json(cls, variant_json: Dict[str, Any]) -> 'SortieVariant':
        return cls(
            mission_type=variant_json.get('missionType', ''),
            modifier_type=variant_json.get('modifierType', ''),
            node=variant_json.get('node', ''),
            tileset=variant_json.get('tileset', '')
        )


@dataclass
class Sortie:
    activation: int
    boss: str
    expiry: int
    extra_drops: List[str]
    reward: str
    seed: int
    twitter: bool
    variants: List[SortieVariant]
    _id: str

    @classmethod
    def parse_sortie(cls, sortie_json: Dict[str, Any]) -> 'Sortie':
        return cls(
            activation=int(sortie_json['Activation']['$date']['$numberLong']),
            expiry=int(sortie_json['Expiry']['$date']['$numberLong']),
            boss=sortie_json.get('Boss', ''),
            extra_drops=sortie_json.get('ExtraDrops', []),
            reward=sortie_json.get('Reward', ''),
            seed=sortie_json.get('Seed', 0),
            twitter=sortie_json.get('Twitter', False),
            variants=[SortieVariant.from_json(variant) for variant in sortie_json.get('Variants', [])],
            _id=sortie_json.get('_id', {}).get('$oid', '')
        )
