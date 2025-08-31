import logging
import time
from typing import Dict, List, Any, Optional

from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse

from backend.helper.helper_function import fetchall
from database.utils.time import get_last_update

router = APIRouter()


# Simple in-process cache (per FastAPI worker)
_CACHE: Dict[str, Any] = {
    "payload": None,  # type: Optional[List[Dict[str, Any]]]
    "last_update": None,  # type: Optional[int]
    "ts": 0.0,  # type: float
}
_CACHE_TTL_SECONDS = 300  # set to 0 to disable TTL and rely solely on last_update


class PrimeStatusService:
    """Get Prime status and parts information from the database efficiently."""

    @staticmethod
    def get_joined_rows() -> List[tuple]:
        """Fetch all sets and their parts in a single JOIN query."""
        return fetchall(
            (
                """
                SELECT vs.warframe_set, vs.vaulted, vs.set_type,
                       pp.id AS part_id, pp.parts_name
                FROM vault_status vs
                LEFT JOIN prime_parts pp ON pp.warframe_set = vs.warframe_set
                ORDER BY vs.warframe_set, pp.parts_name, pp.id
                """
            )
        )

    @staticmethod
    def build_payload(joined_rows: List[tuple]) -> List[Dict[str, Any]]:
        """Group JOIN results by set and build the response payload."""
        result: List[Dict[str, Any]] = []
        current_set: Optional[str] = None
        current_obj: Optional[Dict[str, Any]] = None

        for warframe_set, vaulted, set_type, part_id, parts_name in joined_rows:
            if current_set != warframe_set:
                if current_obj is not None:
                    result.append(current_obj)
                current_set = warframe_set
                current_obj = {
                    "warframe_set": warframe_set,
                    "status": vaulted,
                    "type": set_type,
                    "parts": [],
                }
            if parts_name is not None and part_id is not None:
                current_obj["parts"].append({"parts": parts_name, "id": part_id})

        if current_obj is not None:
            result.append(current_obj)

        # Remove sets that have no parts to preserve prior behavior
        result = [x for x in result if x.get("parts")]
        return result


@router.get("")
def get_prime_status() -> JSONResponse:
    """
    Get all prime set data including:
    - Set name
    - Vault status
    - Type (warframe/weapon/companion)
    - Prime parts information (parts name and id)

    Uses a single JOIN query and an in-memory cache keyed by last_update.
    """
    try:
        # Cache gate using last_update and optional TTL
        now = time.time()
        db_last = get_last_update()

        cached_payload = _CACHE.get("payload")
        cached_last = _CACHE.get("last_update")
        cached_ts = _CACHE.get("ts", 0.0)

        cache_valid = (
            cached_payload is not None
            and cached_last == db_last
            and (_CACHE_TTL_SECONDS <= 0 or (now - cached_ts) < _CACHE_TTL_SECONDS)
        )

        if cache_valid:
            return JSONResponse(content=cached_payload, media_type="application/json")

        # Cache miss: fetch via JOIN and rebuild
        service = PrimeStatusService()
        rows = service.get_joined_rows()
        if not rows:
            raise HTTPException(
                status_code=404, detail="No Prime sets found in the database."
            )

        payload = service.build_payload(rows)
        if not payload:
            raise HTTPException(
                status_code=404, detail="No Prime sets found in the database."
            )

        # Update cache
        _CACHE["payload"] = payload
        _CACHE["last_update"] = db_last
        _CACHE["ts"] = now

        return JSONResponse(content=payload, media_type="application/json")

    except HTTPException:
        raise
    except Exception:
        logging.error("ERROR while fetching Prime status data", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Server error while fetching Prime status data."
        )
