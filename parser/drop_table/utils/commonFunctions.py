import requests
from bs4.element import Tag
from dotenv import load_dotenv

load_dotenv()


def is_empty_row(row: Tag) -> bool:
    return row.get("class") and "blank-row" in row.get("class")


def is_drop_table_available() -> bool:
    return (
        requests.get(
            "https://warframe-web-assets.nyc3.cdn.digitaloceanspaces.com/uploads/cms/hnfvc0o3jnfvc873njb03enrf56.html"
        ).status_code
        == 200
    )
