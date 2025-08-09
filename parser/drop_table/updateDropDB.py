import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

from database.utils.time import get_last_update, update_time
from parser.drop_table.utils.commonFunctions import is_drop_table_available
from parser.drop_table.updater import *

load_dotenv()


# debug function
def generate_debug_time():
    logging.info('MainUpdate: Generating debug time')
    return get_last_update() + 1


class UpdateDropDB:
    def __init__(self) -> None:
        self.body = self.__get_body()
        self.web_update_time = int(datetime.strptime(self.body.find('h3').previous.strip(), "%d %B, %Y").timestamp())
        self.update()


    @staticmethod
    def __get_body():
        url = os.getenv('DROP_TABLE_URL')
        html = requests.get(url)
        soup = BeautifulSoup(html.text, "html.parser")
        return soup.find('body')


    def is_update_needed(self) -> bool:
        logging.info('MainUpdate: Checking if update needed')
        return get_last_update() < self.web_update_time

    def update(self) -> None:
        if not is_drop_table_available():
            logging.error('MainUpdate: Drop table not available')
            return
        if not self.is_update_needed():
            logging.info('MainUpdate: No update needed')
            return
        else:
            logging.info('MainUpdate: Start updating drop_table table')

            h3 = self.body.find_all('h3')[2:]
            tables = self.body.find_all('table')

            for title, table in zip(h3, tables):
                match title.get_text()[:-1]:
                    case 'Missions':
                        UpdateMissionReward(table).run_update()
                    case 'Relics':
                        UpdateRelicReward(table).run_update()
                    case 'Dynamic Location Rewards':
                        UpdateDynamicLocationReward(table).run_update()
                    case 'Sorties':
                        UpdateSortieReward(table).run_update()
                    case 'Cetus Bounty Rewards':
                        UpdateBountyReward(table).run_update()
                    case 'Orb Vallis Bounty Rewards':
                        UpdateBountyReward(table).run_update()
                    case 'Cambion Drift Bounty Rewards':
                        UpdateBountyReward(table).run_update()
                    case 'Zariman Bounty Rewards':
                        UpdateBountyReward(table).run_update()
                    case "Albrecht's Laboratories Bounty Rewards":
                        UpdateBountyReward(table).run_update()
                    case 'Hex Bounty Rewards':
                        UpdateBountyReward(table).run_update()
                    case 'Mod Drops by Source':
                        UpdateModBySource(table).run_update()
                    case 'Mod Drops by Mod':
                        UpdateModByMod(table).run_update()
                    case 'Blueprint/Item Drops by Source':
                        UpdateBlueprintBySource(table).run_update()
                    case 'Blueprint/Item Drops by Blueprint/Item':
                        UpdateBlueprintByItem(table).run_update()
                    case 'Resource Drops by Source':
                        UpdateResourceBySource(table).run_update()
                    case 'Resource Drops by Resource':
                        UpdateResourceByResource(table).run_update()
                    case 'Sigil Drops by Source':
                        UpdateSigilBySource(table).run_update()
                    case 'Additional Item Drops by Source':
                        UpdateAdditionalItemBySource(table).run_update()
                    case 'Relic Drops by Source':
                        UpdateRelicBySource(table).run_update()
                    case 'Keys':
                        UpdateKeyReward(table).run_update()
                    case _:
                        logging.error(f'MainUpdate: Unknown title: {title}')

            update_time(self.web_update_time)
