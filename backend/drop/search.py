from collections import defaultdict, namedtuple
from typing import List, Iterable, TypeVar

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

from backend.helper.helper_function import fetchall

T = TypeVar("T")


def get_available_sets() -> list[str]:
    return [x[0] for x in fetchall('SELECT warframe_set FROM vault_status WHERE status = "1"')]

def make_question_string(l: Iterable[T]) -> str:
    return ','.join('?' for _ in l)


class DropSearchService:
    """"""

    def __init__(self, item_int_arr: List[int]) -> None:
        self.item_int_arr = item_int_arr
        #self.process_search()

    def process_search(self):
        # Step 1: Turn the item list (int) to an item list (str)
        item_arr = self.get_set_list(self.item_int_arr)
        # Step 2: Search item drop
        self.search_item_drop(item_arr)
        # Step 3: Search relic drop
        # Step 4: Return result

    @staticmethod
    def get_set_list(lst: List[int]) -> list[str]:
        """
        Generates a list of strings of part names
        from a database query based on the given list of IDs.

        :param lst: A list of integers representing the IDs to be used in the query.
        :type lst: List[int]
        :return: A list of formatted strings combining valid part names.
        :rtype: list[str]
        """
        place_holder = make_question_string(lst)
        query = f'SELECT warframe_set, parts_name FROM prime_parts WHERE id IN ({place_holder})'
        return [' Prime '.join(x) for x in fetchall(query, lst) if x[0] in get_available_sets()]

    @staticmethod
    def search_item_drop(lst: List[str]) -> dict:
        """
        Searches and organizes items with their drop rates and relics.

        This method processes the given list of item data, where each entry
        contains information about a prize, its relic, drop rate, and whether
        it is radiant. It organizes the data into a dictionary where each key
        is a prize, and the value is a list of unique relics and their associated
        drop rates for that prize. If a new entry has the same relic but a higher
        drop rate, it replaces the existing entry for that relic.

        :param lst: A list of tuples in the format (prize: str, radiant: str,
            drop_rate: float, relic: str), where each tuple contains an item's
            details to be processed.
        :return: A dictionary where each key corresponds to a prize (str), and the
            value is a list of named tuples (relic: str, radiant: str, drop_rate: float)
            containing details about associated relics and their respective drop rates.
        """
        query_result = fetchall(f'SELECT prize, radiant, drop_rate, relic FROM relic_rewards WHERE prize IN ({make_question_string(lst)})', lst)
        ItemDropRate = namedtuple('ItemDropRate', ['relic', 'radiant', 'drop_rate'])
        item_drop = defaultdict(list)

        for prize, radiant, drop_rate, relic in query_result:
            reward = ItemDropRate(relic, radiant, drop_rate)

            existing_relics = [r.relic for r in item_drop[prize]]
            if relic not in existing_relics:
                item_drop[prize].append(reward)
            else:
                for i, existing_reward in enumerate(item_drop[prize]):
                    if existing_reward.relic == relic and drop_rate > existing_reward.drop_rate:
                        item_drop[prize][i] = reward
                        break
        return dict(item_drop)

    @staticmethod
    def search_relic_drop():
        # WIP
        pass


@router.get("")
async def search_drop(lst: List[int]) -> JSONResponse:
    return JSONResponse(DropSearchService(lst).process_search())  # Temp return value for preventing warning
