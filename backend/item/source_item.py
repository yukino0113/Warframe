from typing import Dict, List, Any

from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

from backend.helper.helper_function import fetchall


@router.get("/v1/items/source/{item_id}")
def get_item(item_id: str) -> JSONResponse:
    # item_id is the exact item name (URL-encoded)
    # Fetch relics that can drop_table this item, with refinement breakdown
    rows = fetchall(
        "SELECT relic, radiant, drop_rate FROM relic_rewards WHERE prize = ? ORDER BY relic, radiant",
        (item_id,)
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Item not found")

    by_ref: Dict[str, List[Dict[str, Any]]] = {}
    for relic, radiant, drop_rate in rows:
        by_ref.setdefault(radiant, []).append({
            "relic": relic,
            "chance": float(drop_rate),
        })

    result = {
        "id": item_id,
        "name": item_id,
        "components": [
            {
                "name": item_id,
                "relics": by_ref
            }
        ]
    }
    return JSONResponse(result)
