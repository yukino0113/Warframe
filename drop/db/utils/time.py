from drop.db.WarframeDB import WarframeDB

def get_last_update() -> int:
    return WarframeDB().fetch_all('SELECT * FROM last_update')[0][0]


def update_time(timestamp: int) -> None:
    WarframeDB().execute_query(f'UPDATE last_update SET time = {timestamp}')
