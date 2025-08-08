from dataclasses import dataclass


@dataclass
class RelicReward:
    relic: str
    radiant: str
    price: str
    rarity: str
    drop_rate: float
