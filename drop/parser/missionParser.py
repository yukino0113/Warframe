from drop.utils.commonFunctions import strip_text, is_empty_row
from drop.utils.itemClass import MissionReward


def mission_parser(tables):
    items = []
    # 避免 init 空值錯誤
    location = rotation = ""

    for row in tables.find_all('tr'):
        if title := row.find('th'):
            text = strip_text(title)
            if 'Rotation' not in text:
                location = text
            else:
                rotation = text
        # 檢查空行
        elif not is_empty_row(row):
            price_tag = row.find('td')
            price = strip_text(price_tag)
            rarity_text = strip_text(price_tag.find_next('td'))
            rarity = ' '.join(rarity_text.split(' ')[:-1])
            drop_rate = float(rarity_text.split(' ')[-1][1:-2])

            items.append(MissionReward(price=price, rotation=rotation, rarity=rarity,
                                       drop_rate=drop_rate, location=location))
    return items

