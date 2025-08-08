from drop.parser.commonParser import parse_two_cell_price
from drop.utils.commonFunctions import strip_text, is_empty_row
from drop.utils.itemClass import RelicReward


def relic_parser(tables):
    items = []
    radiant = relic = ""

    for row in tables.find_all('tr'):
        if title := row.find('th'):
            text = strip_text(title)
            relic, radiant = ' '.join(text.split(' ')[:-1]), text.split(' ')[-1].strip('()')

        elif not is_empty_row(row):
            price, rarity, drop_rate = parse_two_cell_price(row.find('td'))
            items.append(RelicReward(price=price, rarity=rarity,
                                     drop_rate=drop_rate, relic=relic, radiant=radiant))
    return items
