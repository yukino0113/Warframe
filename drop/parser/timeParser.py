from bs4.element import Tag
from datetime import datetime
import time


def time_parser(body: Tag) -> int:
    date_str = body.find('h3').previous.strip()
    dt = datetime.strptime(date_str, "%d %B, %Y")
    timestamp = int(time.mktime(dt.timetuple()))
    return timestamp