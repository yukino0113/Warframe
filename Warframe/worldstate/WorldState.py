import json
import urllib.request
from icecream import ic


class WorldState:

    def __init__(self):
        with urllib.request.urlopen('https://content.warframe.com/dynamic/worldState.php') as url:
            data = json.load(url)
            for i in data.keys():
                if i != 'Events':
                    ic(i, data[i])

WorldState()
