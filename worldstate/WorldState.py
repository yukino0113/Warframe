import os
import requests

from dotenv import load_dotenv

from worldstate.utils.ActiveMission import ActiveMission
from worldstate.utils.DailyDeal import DailyDeal
from worldstate.utils.Invasion import Invasion
from worldstate.utils.LiteSortie import LiteSortie
from worldstate.utils.Sortie import Sortie
from worldstate.utils.SyndicateMission import SyndicateMission
from worldstate.utils.Voidstorm import VoidStorm

load_dotenv()

var = ['WorldSeed',
       'Version',
       'MobileVersion',
       'BuildLabel',
       # 'Time',
       'Events',
       'Goals',
       'Alerts',
       # 'Sorties',
       # 'LiteSorties',
       # 'SyndicateMissions',
       # 'ActiveMissions',
       'GlobalUpgrades',
       'FlashSales',
       'InGameMarket',
       # 'Invasions',
       'HubEvents',
       'NodeOverrides',
       'VoidTraders',
       'PrimeVaultTraders',
       # 'VoidStorms',
       'PrimeAccessAvailability',
       'PrimeVaultAvailabilities',
       'PrimeTokenAvailability',
       # 'DailyDeals',
       'LibraryInfo',
       'PVPChallengeInstances',
       'PersistentEnemies',
       'PVPAlternativeModes',
       'PVPActiveTournaments',
       'ProjectPct',
       'ConstructionProjects',
       'TwitchPromos',
       'ExperimentRecommended',
       'EndlessXpChoices',
       'ForceLogoutVersion',
       'FeaturedGuilds',
       'SeasonInfo',
       'KnownCalendarSeasons',
       'Tmp']

class WorldState:

    def __init__(self):
        self.url = os.getenv('WORLD_STATE_URL')
        self.json = requests.get(self.url).json()

        self.time = self.json['Time']
        self.active_mission = [ActiveMission.parse_active_mission(x) for x in self.json['ActiveMissions']]
        self.syndicate_mission = [SyndicateMission.parse_syndicate(x) for x in self.json['SyndicateMissions']]
        self.sortie = [Sortie.parse_sortie(x) for x in self.json['Sorties']]
        self.lite_sortie = [LiteSortie.parse_lite_sortie(x) for x in self.json['LiteSorties']]
        self.invasion = [Invasion.parse_invasion(x) for x in self.json['Invasions']]
        self.void_storm = [VoidStorm.parse_void_storm(x) for x in self.json['VoidStorms']]
        self.daily_deal = [DailyDeal.parse_daily_deal(x) for x in self.json['DailyDeals']]


