from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class VoidStorm:
    activation: int
    active_mission_tier: str
    expiry: int
    node: str
    _id: str

    @classmethod
    def parse_void_storm(cls, storm_json: Dict[str, Any]) -> 'VoidStorm':
        return cls(
            activation=int(storm_json['Activation']['$date']['$numberLong']),
            active_mission_tier=storm_json.get('ActiveMissionTier', ''),
            expiry=int(storm_json['Expiry']['$date']['$numberLong']),
            node=storm_json.get('Node', ''),
            _id=storm_json.get('_id', {}).get('$oid', '')
        )