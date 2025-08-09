from dataclasses import dataclass
from typing import List, Dict, Any

"""
Example JSON:
{
    'Activation': {'$date': {'$numberLong': '1754409542740'}},
    'Expiry': {'$date': {'$numberLong': '1754495940000'}},
    'Nodes': ['SolNode79',
            'SolNode128',
            'SettlementNode1',
            'SolNode42',
            'SolNode138',
            'SolNode195',
            'SolNode126'],
    'Seed': 25131,
    'Tag': 'ArbitersSyndicate',
    '_id': {'$oid': '68922a46c6fb3a1779c59f36'}
}
"""


@dataclass
class SyndicateMission:
    activation: int
    expiry: int
    nodes: List[str]
    seed: int
    tag: str
    _id: str

    @classmethod
    def parse_syndicate(cls, mission_json: Dict[str, Any]) -> 'SyndicateMission':
        return cls(
            activation=int(mission_json['Activation']['$date']['$numberLong']),
            expiry=int(mission_json['Expiry']['$date']['$numberLong']),
            nodes=mission_json.get('Nodes', []),
            seed=mission_json.get('Seed', 0),
            tag=mission_json.get('Tag', ''),
            _id=mission_json.get('_id', {}).get('$oid', '')
        )
