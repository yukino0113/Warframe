from dataclasses import dataclass

@dataclass
class MissionReward:
    source: str
    rotation: str
    price: str
    rarity: str
    drop_rate: float


@dataclass
class RelicReward:
    relic: str
    radiant: str
    price: str
    rarity: str
    drop_rate: float
