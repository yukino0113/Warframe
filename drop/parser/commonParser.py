from bs4.element import Tag


def strip_text(text: Tag) -> str:
    return text.get_text().strip()



def parse_two_cell_price(price_tag: Tag) -> list:
    price_text = strip_text(price_tag)
    words = strip_text(price_tag.find_next('td')).split(' ')
    return [price_text, ' '.join(words[:-1]), words[-1][1:-2]]


def parse_three_cell_price(first_td: Tag) -> list:
    """
    Parses a 3-column data row where the structure is:
    [blank-or-pad td] [item/mod/resource/etc td] [rarity-with-percent td]
    Returns [item_text, rarity_label, drop_rate_float]
    """
    item_td = first_td.find_next('td')
    rarity_td = item_td.find_next('td')
    price_text = strip_text(item_td)
    words = strip_text(rarity_td).split(' ')
    return [price_text, ' '.join(words[:-1]), words[-1][1:-2]]


def parse_row_source_chance(first_td: Tag) -> list:
    """
    Parses a 3-column data row where the structure is:
    [source td] [drop chance td - ignored] [rarity-with-percent td]
    Returns [source_text, rarity_label, drop_rate_float]
    """
    source_text = strip_text(first_td)
    # skip the middle chance cell
    chance_td = first_td.find_next('td')
    rarity_td = chance_td.find_next('td')
    words = strip_text(rarity_td).split(' ')
    return [source_text, ' '.join(words[:-1]), words[-1][1:-2]]
