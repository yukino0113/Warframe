from drop.utils.commonFunctions import strip_text, is_empty_row
from drop.utils.itemClass import RelicReward


def relic_parser(tables):
    items = []
    # 避免 init 空值錯誤
    rotation = radiant = relic = ""

    for row in tables.find_all('tr'):
        if title := row.find('th'):
            raw_text = strip_text(title)
            text = ' '.join(raw_text.split(' ')[:-1])
            radiant = raw_text.split(' ')[-1].strip('()')
            if 'Rotation' not in text:
                relic = text
            else:
                rotation = text
        # 檢查空行
        elif not is_empty_row(row):
            price_tag = row.find('td')
            price = strip_text(price_tag)
            rarity_text = strip_text(price_tag.find_next('td'))
            rarity = ' '.join(rarity_text.split(' ')[:-1])
            drop_rate = float(rarity_text.split(' ')[-1][1:-2])

            items.append(RelicReward(price=price, rotation=rotation, rarity=rarity,
                                     drop_rate=drop_rate, relic=relic, radiant=radiant))
    return items
