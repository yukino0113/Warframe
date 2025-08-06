from dataclasses import dataclass
from typing import Dict, Any

"""
Example JSON:
{
    'Activation': {'$date': {'$numberLong': '1754462402005'}},
    'Expiry': {'$date': {'$numberLong': '1754469441143'}},
    'Hard': True,
    'MissionType': 'MT_SABOTAGE',
    'Modifier': 'VoidT4',
    'Node': 'SolNode404',
    'Region': 15,
    'Seed': 49547,
    '_id': {'$oid': '6892f8c20c00cf1624c59f36'}}
"""

@dataclass
class ActiveMission:
    activation: int
    expiry: int
    hard: bool
    mission_type: str
    modifier: str
    node: str
    region: int
    seed: int
    _id: str

    @classmethod
    def parse_active_mission(cls, mission_json: Dict[str, Any]) -> 'ActiveMission':
        return cls(
            activation=int(mission_json['Activation']['$date']['$numberLong']),
            expiry=int(mission_json['Expiry']['$date']['$numberLong']),
            hard=mission_json.get('Hard', False),
            mission_type=mission_json['MissionType'],
            modifier=mission_json['Modifier'],
            node=mission_json['Node'],
            region=mission_json['Region'],
            seed=mission_json['Seed'],
            _id=mission_json['_id']['$oid']
        )