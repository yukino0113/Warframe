from dataclasses import dataclass
from typing import List, Tuple

from bs4.element import Tag

from parser.drop_table.utils.commonParser import parse_three_cell_prize, strip_text
from parser.drop_table.utils.commonFunctions import is_empty_row
from .base_updater import BaseUpdater


@dataclass
class BountyReward:
    source: str  # e.g., "Level 5 - 15 Cetus Bounty"
    rotation: str  # e.g., "Rotation A"
    stage: str  # e.g., "Stage 1" or "Stage 2, Stage 3 of 4, and Stage 3 of 5"
    prize: str
    rarity: str
    drop_rate: float


class UpdateBountyReward(BaseUpdater):
    """
    Generic updater for all Open World Bounty sections (Cetus, Orb Vallis, Cambion Drift,
    Zariman, Albrecht's Laboratories, Hex). The parser is the same across them.
    """

    def get_table_name(self) -> str:
        return 'bounty_rewards'

    def get_table_schema(self) -> List[str]:
        return [
            'id INTEGER PRIMARY KEY AUTOINCREMENT',
            'prize TEXT NOT NULL',
            'rotation TEXT NOT NULL',
            'stage TEXT NOT NULL',
            'rarity TEXT NOT NULL',
            'drop_rate DECIMAL(5,4) NOT NULL',
            'source TEXT NOT NULL',
            'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        ]

    def get_columns(self) -> List[str]:
        return ['prize', 'rotation', 'stage', 'rarity', 'drop_rate', 'source']

    def extract_values(self, reward: BountyReward) -> Tuple:
        return reward.prize, reward.rotation, reward.stage, reward.rarity, reward.drop_rate, reward.source

    def _parse_data(self) -> List[BountyReward]:
        items: List[BountyReward] = []
        source = rotation = stage = ""

        def handle_header_row(th_row: Tag):
            nonlocal source, rotation, stage
            ths = th_row.find_all('th')
            # Header types can be:
            # - Level X - Y Cetus Bounty (colspan=3) -> source
            # - Rotation A (colspan=3) -> rotation
            # - Stage X (colspan=2) -> stage, often preceded by a pad cell td
            text = strip_text(ths[0]) if ths else ''
            if 'Rotation' in text:
                rotation = text
            elif 'Stage' in text:
                # The stage header can be in second th if a pad-cell td exists
                stage = strip_text(ths[-1])
            else:
                source = text

        for row in self.tables.find_all('tr'):
            if row.find('th'):
                handle_header_row(row)
            elif not is_empty_row(row):
                prize, rarity, drop_rate = parse_three_cell_prize(row.find('td'))
                items.append(BountyReward(
                    source=source,
                    rotation=rotation,
                    stage=stage,
                    prize=prize,
                    rarity=rarity,
                    drop_rate=drop_rate
                ))
        return items
