from typing import List, Dict, Any
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from backend.API_main import app
from backend.helper.helper_function import fetchall


@app.get("/v1/relics/{relic_id}/where-to-get")
def get_relic_sources(relic_id: str) -> JSONResponse:
    results: List[Dict[str, Any]] = []
    # Missions
    rows = fetchall(
        "SELECT source, rotation, drop_rate FROM mission_rewards WHERE price = ?",
        (relic_id,)
    )
    for source, rotation, drop_rate in rows:
        results.append({
            "type": "mission",
            "source": source,
            "rotation": rotation,
            "stage": None,
            "chance": float(drop_rate),
            "est_time": None,
        })
    # Bounties
    rows = fetchall(
        "SELECT source, rotation, stage, drop_rate FROM bounty_rewards WHERE price = ?",
        (relic_id,)
    )
    for source, rotation, stage, drop_rate in rows:
        results.append({
            "type": "bounty",
            "source": source,
            "rotation": rotation,
            "stage": stage,
            "chance": float(drop_rate),
            "est_time": None,
        })
    # Dynamic locations
    rows = fetchall(
        "SELECT source, rotation, drop_rate FROM dynamic_location_rewards WHERE price = ?",
        (relic_id,)
    )
    for source, rotation, drop_rate in rows:
        results.append({
            "type": "dynamic",
            "source": source,
            "rotation": rotation,
            "stage": None,
            "chance": float(drop_rate),
            "est_time": None,
        })
    # Fallback: generic sources (no rotation/stage)
    try:
        rows = fetchall(
            "SELECT source, rarity, drop_rate FROM relic_drops_by_source WHERE item = ?",
            (relic_id,)
        )
        for source, rarity, drop_rate in rows:
            results.append({
                "type": "generic",
                "source": source,
                "rotation": None,
                "stage": None,
                "rarity": rarity,
                "chance": float(drop_rate),
                "est_time": None,
            })
    except Exception:
        pass

    if not results:
        raise HTTPException(status_code=404, detail="No sources found for this relic")

    return JSONResponse(results)
