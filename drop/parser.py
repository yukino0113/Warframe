import requests
import os
from bs4 import BeautifulSoup
from icecream import ic
from dotenv import load_dotenv
load_dotenv()

class Parser:
    def __init__(self):
        self.url = os.getenv('DROP_TABLE_URL')
        self.html = requests.get(self.url)
        self.soup = BeautifulSoup(self.html.text, "html.parser")

        self.body = self.soup.find('body')
        ic(self.body.find('p'))



        #def get_last_update(self):




