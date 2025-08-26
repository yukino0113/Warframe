from collections import defaultdict, namedtuple
from typing import List, Iterable, TypeVar

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from database.schema import RewardTables

router = APIRouter()

from backend.helper.helper_function import fetchall

T = TypeVar("T")


def get_available_sets() -> list[str]:
    return [
        x[0]
        for x in fetchall('SELECT warframe_set FROM vault_status WHERE valuted = "0"')
    ]


def make_question_string(l: Iterable[T]) -> str:
    return ",".join("?" for _ in l)


class DropSearchService:
    """
    Handles operations related to searching and scoring item drops, including fetching
    data from external sources, organizing drop information, and calculating scores
    for relics and source areas.

    This class is designed for processing item drop data in a structured and efficient
    manner. It provides methods to convert item data into specific formats, search for
    item drops, calculate relic scores based on drop rates, and aggregate area-based
    drop scores. The functionality is encapsulated into steps for easier adjustment
    and extension.

    :ivar item_int_arr: A list of integers representing the item IDs to process.
    :type item_int_arr: List[int]
    """

    def __init__(self, item_int_arr: List[int]) -> None:
        self.item_int_arr = item_int_arr
        self.process_search()

    def process_search(self):
        # Step 1: Turn the item list (int) to an item list (str)
        item_list = self.get_set_list(self.item_int_arr)
        # Step 2: Search item drop
        relic_list = self.search_item_drop(item_list)
        # Step 3: Get relics score
        relic_score_list = self.get_relic_score_list(relic_list)
        # Step 4: Get relic drops
        area_score_list = self.get_area_score_list(relic_score_list)
        # Step 5: Organize data
        return {"relic_score": relic_score_list, "area_score": area_score_list}

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
        query = f"SELECT warframe_set, parts_name FROM prime_parts WHERE id IN ({place_holder})"
        result = [x for x in fetchall(query, lst) if x[0] in get_available_sets()]

        stringify = [
            (
                f"{x[0]} Prime {x[1]} Blueprint"
                if x[1] in ["Chassis", "Neuroptics", "Systems"]
                else f"{x[0]} Prime {x[1]}"
            )
            for x in result
        ]

        return stringify

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
        query_result = fetchall(
            f"SELECT prize, radiant, drop_rate, relic FROM relic_rewards WHERE prize IN ({make_question_string(lst)})",
            lst,
        )
        ItemDropRate = namedtuple("ItemDropRate", ["relic", "radiant", "drop_rate"])
        item_drop = defaultdict(list)

        for prize, radiant, drop_rate, relic in query_result:
            reward = ItemDropRate(relic, radiant, drop_rate)
            existing_relics = [r.relic for r in item_drop[prize]]
            if relic not in existing_relics:
                item_drop[prize].append(reward)
            else:
                for i, existing_reward in enumerate(item_drop[prize]):
                    if (
                        existing_reward.relic == relic
                        and drop_rate > existing_reward.drop_rate
                    ):
                        item_drop[prize][i] = reward
                        break
        return dict(item_drop)

    @staticmethod
    def get_relic_score_list(item_drop_list: dict):
        """
        Processes a list of item drops to calculate and organize relic scores and their associated
        item list. Each item drop rate is used to increment the score of its corresponding relic,
        grouping items by their relics in a structured dictionary.

        :param item_drop_list: A dictionary representing item drops where keys are item names
            and values are lists of drop rate objects.
        :return: A dictionary containing relic names as keys. Each relic key has a value of another
            dictionary that includes a 'score' field for the relic's accumulated score, and an
            'item_list' field with the corresponding items.
        """
        relic_list = {}
        for item_name, drop_rates in item_drop_list.items():
            for drop_rate in drop_rates:
                relic_name = drop_rate.relic
                if relic_name not in relic_list:
                    relic_list[relic_name] = {"score": 0, "item_list": []}
                relic_list[relic_name]["score"] += drop_rate.drop_rate
                relic_list[relic_name]["item_list"].append(item_name)

        return relic_list

    @staticmethod
    def get_area_score_list(item_score_list: dict) -> dict:
        """
        Calculates and returns a dictionary mapping source areas to their respective drop
        scores and categorized rotation details based on relic drop rates.

        :param item_score_list: A dictionary where keys are item names and values are their scores.
        :type item_score_list: dict
        :return: A dictionary mapping each source area to its cumulative drop score and detailed
                 rotation-related information, including scores and lists of relics per rotation.
        :rtype: dict
        """
        area_list = {}
        for table in RewardTables.TABLES:
            relics = list(item_score_list.keys())
            query = f"SELECT prize, drop_rate, source, rotation FROM {table.__tablename__} WHERE prize IN ({make_question_string(relics)})"
            for prize, drop_rate, source, rotation in fetchall(query, relics):
                if source not in area_list:
                    area_list[source] = {
                        "score": 0,
                        "A": {"score": 0, "relic_list": []},
                        "B": {"score": 0, "relic_list": []},
                        "C": {"score": 0, "relic_list": []},
                    }

                rotations = rotation.split(" ")[-1]
                area_list[source]["score"] += drop_rate
                area_list[source][rotations]["score"] += drop_rate
                area_list[source][rotations]["relic_list"].append(prize)
        return area_list


class SearchRequest(BaseModel):
    data: List[int]


@router.post("")
async def search_drop(request: SearchRequest) -> JSONResponse:

    try:
        return JSONResponse(DropSearchService(request.data).process_search())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
