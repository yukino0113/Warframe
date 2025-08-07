from dataclasses import dataclass

@dataclass
class MissionReward:
    price: str
    rotation: str
    rarity: str
    drop_rate: float
    location: str


@dataclass
class RelicReward:
    price: str
    radiant: str
    rotation: str
    rarity: str
    drop_rate: float
    relic: str
