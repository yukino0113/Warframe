from bs4.element import Tag


def time_parser(body: Tag) -> str:
    return body.find('p').getText().strip().split('\n')[-1].strip()