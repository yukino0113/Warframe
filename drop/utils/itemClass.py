from dataclasses import dataclass

@dataclass
class MissionReward:
    name: str
    rotation: str
    rarity: str
    drop_rate: float
    location: str