from typing import Dict, List, Any

from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

from backend.helper.helper_function import fetchall, split_relic_name


@router.get("/v1/relics/prize/{relic_id}")
def get_relic_prize(relic_id: str) -> JSONResponse:
    if 'Relic' not in relic_id:
        relic_id = f'{relic_id} Relic'

    rows = fetchall(
        "SELECT prize, radiant, rarity, drop_rate FROM relic_rewards WHERE relic = ? ORDER BY radiant",
        (relic_id,)
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Relic not found")
    by_ref: Dict[str, List[Dict[str, Any]]] = {}
    for prize, radiant, rarity, drop_rate in rows:
        by_ref.setdefault(radiant, []).append({
            "item": prize,
            "chance": float(drop_rate),
        })

    split_relic_name(relic_id)

    return JSONResponse({
        "relic": relic_id,
        "rewards": by_ref,
    })
