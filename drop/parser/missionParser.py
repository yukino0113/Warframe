from drop.parser.commonParser import parse_two_cell_price
from drop.utils.commonFunctions import strip_text, is_empty_row
from drop.utils.itemClass import MissionReward


def mission_parser(tables):
    items = []
    source = rotation = ""

    for row in tables.find_all('tr'):
        if title := row.find('th'):
            text = strip_text(title)
            rotation = text if 'Rotation' in text else rotation
            source = text if 'Rotation' not in text else source

        elif not is_empty_row(row):
            price, rarity, drop_rate = parse_two_cell_price(row.find('td'))
            items.append(MissionReward(source=source, rotation=rotation, price=price, rarity=rarity,
                                       drop_rate=drop_rate))
    return items
