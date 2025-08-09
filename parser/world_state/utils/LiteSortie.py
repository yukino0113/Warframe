from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class LiteSortieMission:
    mission_type: str
    node: str

    @classmethod
    def from_json(cls, mission_json: Dict[str, Any]) -> 'LiteSortieMission':
        return cls(
            mission_type=mission_json.get('missionType', ''),
            node=mission_json.get('node', '')
        )


@dataclass
class LiteSortie:
    activation: int
    boss: str
    expiry: int
    missions: List[LiteSortieMission]
    reward: str
    seed: int
    _id: str

    @classmethod
    def parse_lite_sortie(cls, sortie_json: Dict[str, Any]) -> 'LiteSortie':
        missions = [
            LiteSortieMission.from_json(mission)
            for mission in sortie_json.get('Missions', [])
        ]

        return cls(
            activation=int(sortie_json['Activation']['$date']['$numberLong']),
            expiry=int(sortie_json['Expiry']['$date']['$numberLong']),
            boss=sortie_json.get('Boss', ''),
            missions=missions,
            reward=sortie_json.get('Reward', ''),
            seed=sortie_json.get('Seed', 0),
            _id=sortie_json.get('_id', {}).get('$oid', '')
        )
