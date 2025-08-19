from typing import List

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

from backend.helper.helper_function import fetchall


def get_available_sets() -> List[str]:
    return [x[0] for x in fetchall('SELECT warframe_set FROM vault_status WHERE status = "1"')]


class DropSearchService:
    """"""

    def __init__(self, item_int_arr: List[int]) -> None:
        self.item_int_arr = item_int_arr
        self.process_search()

    def process_search(self):
        # Step 1: Turn the item list (int) to an item list (str)
        item_arr = self.get_set_list(self.item_int_arr)
        # Step 2: Search item drop
        self.search_item_drop(item_arr)
        # Step 3: Search relic drop
        # Step 4: Return result

    @staticmethod
    def get_set_list(lst: List[int]) -> list[str]:
        place_holder = ','.join('?' for _ in lst)
        query = f'SELECT warframe_set, parts_name FROM prime_parts WHERE id IN ({place_holder})'
        return [' Prime '.join(x) for x in fetchall(query, lst) if x[0] in get_available_sets()]

    @staticmethod
    def search_item_drop(lst: List[str]) -> List[tuple]:
        # WIP
        pass

    @staticmethod
    def search_relic_drop():
        # WIP
        pass


@router.get("")
async def search_drop(lst: List[int]) -> JSONResponse:
    return JSONResponse(DropSearchService(lst).process_search())  # Temp return value for preventing warning
