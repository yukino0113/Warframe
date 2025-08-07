import logging
import requests
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from db.time import get_last_update, update_time
from drop.parser.timeParser import *

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



    def update(self):
        if not self.is_update_needed():
            logging.info('MainUpdate: No update needed')
        else:
            logging.info('MainUpdate: Updating drop table')
            update_time(generate_debug_time())


