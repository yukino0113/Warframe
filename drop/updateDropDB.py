import logging
from bs4 import BeautifulSoup

from db.time import get_last_update, update_time
from drop.parser.timeParser import *
from drop.parser.missionParser import *
from drop.parser.relicParser import *
from drop.utils.commonFunctions import *
from db.mission_reward import *
from db.relic import *

load_dotenv()


# debug function
def generate_debug_time():
    logging.info('MainUpdate: Generating debug time')
    return get_last_update() + 1


class UpdateDropDB:
    def __init__(self) -> None:
        self.body = self.__get_body()
        self.web_update_time = time_parser(self.body)
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
            logging.info('MainUpdate: Start updating drop table')

            h3 = self.body.find_all('h3')[2:]
            tables = self.body.find_all('table')

            for title, table in zip(h3, tables):
                match title.get_text()[:-1]:
                    case 'Missions':
                        delete_mission_reward_table()
                        create_mission_reward_table()
                        update_mission_rewards(mission_parser(table))
                    case 'Relics':
                        delete_relic_reward_table()
                        create_relic_reward_table()
                        update_relic_rewards(relic_parser(table))
                    case 'Keys':
                        pass
                    case _:
                        logging.warning(f'MainUpdate: Unknown title: {title}')

            update_time(generate_debug_time())
