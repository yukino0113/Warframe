import requests
from bs4.element import Tag
from dotenv import load_dotenv
import os
load_dotenv()


def strip_text(text: Tag) -> str:
    return text.getText().strip()


def is_empty_row(row: Tag) -> bool:
    return row.get('class') and 'blank-row' in row.get('class')


def is_drop_table_available() -> bool:
    return requests.get(os.getenv('DROP_TABLE_URL')).status_code == 200