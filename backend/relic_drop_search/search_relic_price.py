from typing import Dict, List, Any
from fastapi.responses import JSONResponse
from fastapi import HTTPException

from backend.API_main import app
from backend.helper.helper_function import fetchall, split_relic_name


@app.get("/v1/relics/{relic_id}")
def get_relic_price(relic_id: str) -> JSONResponse:
    if 'Relic' not in relic_id:
        relic_id = f'{relic_id} Relic'

    rows = fetchall(
        "SELECT price, radiant, rarity, drop_rate FROM relic_rewards WHERE relic = ? ORDER BY radiant",
        (relic_id,)
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Relic not found")
    by_ref: Dict[str, List[Dict[str, Any]]] = {}
    for price, radiant, rarity, drop_rate in rows:
        by_ref.setdefault(radiant, []).append({
            "item": price,
            "chance": float(drop_rate),
        })
    meta = split_relic_name(relic_id)
    return JSONResponse({
        "relic": relic_id,
        "rewards": by_ref,
    })
