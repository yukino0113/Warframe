import logging
from datetime import datetime
from bs4 import BeautifulSoup

from drop.db.utils.time import get_last_update, update_time
from drop.utils.commonFunctions import *
from drop.varities import *

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
            logging.info('MainUpdate: Start updating drop table')

            h3 = self.body.find_all('h3')[2:]
            tables = self.body.find_all('table')

            for title, table in zip(h3, tables):
                match title.get_text()[:-1]:
                    case 'Missions':
                        UpdateMissionReward(table).run_update()
                    case 'Relics':
                        UpdateRelicReward(table).run_update()
                    case 'Keys':
                        pass
                    case _:
                        logging.warning(f'MainUpdate: Unknown title: {title}')

            update_time(generate_debug_time())
