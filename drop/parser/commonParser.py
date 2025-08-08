from bs4.element import Tag


def strip_text(text: Tag) -> str:
    return text.get_text().strip()





def parse_two_cell_price(price_tag: Tag) -> list:
    price_text = strip_text(price_tag)
    words = strip_text(price_tag.find_next('td')).split(' ')
    return [price_text, ' '.join(words[:-1]), words[-1][1:-2]]


def parse_three_cell_price():
    pass
