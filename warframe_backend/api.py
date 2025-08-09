import os
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from drop.db.WarframeDB import WarframeDB
import utils.logger  # noqa: F401 - initialize logging formatting

app = FastAPI(title="Warframe Drop API", version="v1")


# ---- Helpers ----

def fetchall(query: str, params: Optional[tuple] = None) -> List[tuple]:
    db = WarframeDB()
    cur = db.cursor
    try:
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        rows = cur.fetchall()
    finally:
        db.conn.close()
    return rows


def detect_type(item_name: str) -> str:
    name = item_name.lower()
    warframe_keys = ["neuroptics", "systems", "chassis"]
    weapon_keys = [
        "barrel", "receiver", "stock", "blade", "handle", "grip", "string",
        "link", "guard", "ornament", "hilt", "stars", "lower limb", "upper limb",
    ]
    if any(k in name for k in warframe_keys):
        return "warframe_component"
    if any(k in name for k in weapon_keys):
        return "weapon_component"
    # blueprint only -> ambiguous; leave generic
    return "component"


def split_relic_name(relic: str) -> Dict[str, str]:
    parts = relic.split()
    return {
        "era": parts[0] if len(parts) > 0 else "",
        "code": parts[1] if len(parts) > 1 else "",
        "name": relic,
    }


def load_exclude_keywords() -> List[str]:
    """
    Returns a list of lowercase keywords to filter out (e.g., ['kuva']).
    Priority:
      1) config/filter_keywords.txt (one keyword per line, supports comments starting with '#')
      2) environment variable EXCLUDE_KEYWORDS (comma-separated)
      3) default empty list
    """
    keywords: List[str] = []
    # 1) file
    cfg_path = os.getenv("FILTER_KEYWORDS_FILE", os.path.join("config", "filter_keywords.txt"))
    try:
        if os.path.isfile(cfg_path):
            with open(cfg_path, "r", encoding="utf-8") as f:
                for line in f:
                    s = line.strip()
                    if not s or s.startswith("#"):
                        continue
                    keywords.append(s.lower())
    except Exception:
        # if reading fails, ignore and fallback to env
        pass
    # 2) env
    if not keywords:
        env_val = os.getenv("EXCLUDE_KEYWORDS", "")
        if env_val:
            keywords = [k.strip().lower() for k in env_val.split(",") if k.strip()]
    return keywords


def is_excluded(text: str, words: List[str]) -> bool:
    t = text.lower()
    return any(w in t for w in words)


def get_available_relics() -> set:
    """
    Return the set of relic names that are currently obtainable from sources AND that contain
    at least one Warframe component (Neuroptics/Systems/Chassis) in their reward tables.
    Additionally, apply a simple keyword exclusion (e.g., 'kuva') against reward item names.
    """
    # Collect currently dropping relics from source tables
    relics_mission = {r[0] for r in
                      fetchall("SELECT price FROM mission_rewards WHERE price LIKE '% %%' GROUP BY price")}
    relics_bounty = {r[0] for r in fetchall("SELECT price FROM bounty_rewards WHERE price LIKE '% %%' GROUP BY price")}
    relics_dynamic = {r[0] for r in
                      fetchall("SELECT price FROM dynamic_location_rewards WHERE price LIKE '% %%' GROUP BY price")}
    try:
        relics_by_source = {r[0] for r in fetchall("SELECT item FROM relic_drops_by_source GROUP BY item")}
    except Exception:
        relics_by_source = set()
    available_candidates = relics_mission | relics_bounty | relics_dynamic | relics_by_source

    # Load exclusions
    exclude_words = load_exclude_keywords()

    # Limit to relics that actually have Warframe component rewards (and not excluded by keywords)
    warframe_relics: set = set()
    # Pull rewards for all candidate relics in one go, then filter
    if available_candidates:
        qmarks = ",".join(["?"] * len(available_candidates))
        rows = fetchall(
            f"SELECT relic, price FROM relic_rewards WHERE relic IN ({qmarks})",
            tuple(available_candidates)
        )
        # For each relic, check if it has a warframe component reward not excluded
        for relic_name, price in rows:
            if is_excluded(price, exclude_words):
                continue
            if detect_type(price) == "warframe_component":
                warframe_relics.add(relic_name)

    return available_candidates & warframe_relics


def get_available_warframe() -> List[str]:
    """
    Return a list of Warframe set names (e.g., "Wisp Prime") that are currently obtainable
    via relics which drop at least one of the three core components: Neuroptics, Systems, Chassis.
    Uses get_available_relics() to limit to currently available relics.
    """
    available_relics = get_available_relics()
    if not available_relics:
        return []

    # Find rewards from those relics that are Warframe components we care about
    qmarks = ",".join(["?"] * len(available_relics))
    rows = fetchall(
        f"""
        SELECT price FROM relic_rewards
        WHERE relic IN ({qmarks})
          AND (
                LOWER(price) LIKE '% neuroptics blueprint'
             OR LOWER(price) LIKE '% systems blueprint'
             OR LOWER(price) LIKE '% chassis blueprint'
          )
        """,
        tuple(available_relics)
    )

    # From e.g., "Wisp Prime Neuroptics" -> "Wisp Prime"
    suffixes = [" neuroptics blueprint", " system blueprints", " chassis blueprint"]
    names: set = set()
    for (price,) in rows:
        p = price.strip()
        pl = p.lower()
        for s in suffixes:
            if pl.endswith(s):
                base = p[: -len(s)].strip()
                if base:
                    names.add(base)
                break

    return sorted(names)


# ---- Items Endpoints ----

@app.get("/v1/items")
def list_items(type: Optional[str] = Query(None, pattern="^(warframe|weapon)$"),
               search: Optional[str] = None,
               platform: Optional[str] = None) -> JSONResponse:
    """
    Returns list of items (from blueprint_drops_by_item) with ids, type guess, and vaulted status.
    """
    where = []
    params: List[Any] = []
    if search:
        where.append("LOWER(item) LIKE ?")
        params.append(f"%{search.lower()}%")
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    rows = fetchall(f"SELECT item FROM blueprint_drops_by_item {where_sql} GROUP BY item ORDER BY item",
                    tuple(params) if params else None)

    available_relics = get_available_relics()

    results = []
    for (item_name,) in rows:
        itype = detect_type(item_name)
        if type:
            mapped = "warframe_component" if type == "warframe" else "weapon_component"
            if itype != mapped:
                # allow generic component to pass only if no filter
                continue
        # Determine vault status by checking relics that drop this item, and whether any of those relics are available
        relic_rows = fetchall("SELECT relic FROM relic_rewards WHERE price = ? GROUP BY relic", (item_name,))
        relic_names = [r[0] for r in relic_rows]
        vaulted = True
        for relic in relic_names:
            if relic in available_relics:
                vaulted = False
                break
        results.append({
            "id": item_name,  # use name as ID for MVP
            "name": item_name,
            "type": itype,
            "vaulted": vaulted,
        })
    return JSONResponse(results)


@app.get("/v1/items/{item_id}")
def get_item(item_id: str) -> JSONResponse:
    # item_id is the exact item name (URL-encoded)
    # Fetch relics that can drop this item, with refinement breakdown
    rows = fetchall(
        "SELECT relic, radiant, rarity, drop_rate FROM relic_rewards WHERE price = ? ORDER BY relic, radiant",
        (item_id,)
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Item not found")

    by_ref: Dict[str, List[Dict[str, Any]]] = {}
    for relic, radiant, rarity, drop_rate in rows:
        by_ref.setdefault(radiant, []).append({
            "relic": relic,
            "rarity": rarity,
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


@app.get("/v1/items/{item_id}/components")
def get_item_components(item_id: str) -> JSONResponse:
    rows = fetchall(
        "SELECT relic, radiant, rarity, drop_rate FROM relic_rewards WHERE price = ? ORDER BY relic, radiant",
        (item_id,)
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Item not found")
    flat = [
        {
            "component": item_id,
            "relic": relic,
            "refinement": radiant,
            "rarity": rarity,
            "chance": float(drop_rate),
        } for relic, radiant, rarity, drop_rate in rows
    ]
    return JSONResponse(flat)


# ---- Relics Endpoints ----

@app.get("/v1/relics")
def list_relics(era: Optional[str] = None,
                search: Optional[str] = None,
                vaulted: Optional[bool] = None) -> JSONResponse:
    where = []
    params: List[Any] = []
    # Distinct relics from rewards table
    if era:
        where.append("LOWER(relic) LIKE ?")
        params.append(f"{era.lower()} %")
    if search:
        where.append("LOWER(relic) LIKE ?")
        params.append(f"%{search.lower()}%")
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    rows = fetchall(f"SELECT relic FROM relic_rewards {where_sql} GROUP BY relic ORDER BY relic",
                    tuple(params) if params else None)

    available_relics = get_available_relics()

    items = []
    for (relic_name,) in rows:
        meta = split_relic_name(relic_name)
        is_vaulted = relic_name not in available_relics
        if vaulted is not None and is_vaulted != vaulted:
            continue
        # simple reward summary: count by rarity over Intact (or overall)
        reward_rows = fetchall("SELECT rarity FROM relic_rewards WHERE relic = ?", (relic_name,))
        rarity_counts: Dict[str, int] = {}
        for (rarity,) in reward_rows:
            rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
        items.append({
            "id": relic_name,
            "era": meta["era"],
            "code": meta["code"],
            "vaulted": is_vaulted,
            "reward_summary": rarity_counts,
        })

    return JSONResponse(items)


@app.get("/v1/relics/{relic_id}")
def get_relic(relic_id: str) -> JSONResponse:
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
            "rarity": rarity,
            "chance": float(drop_rate),
        })
    meta = split_relic_name(relic_id)
    return JSONResponse({
        "id": relic_id,
        "era": meta["era"],
        "code": meta["code"],
        "rewards": by_ref,
    })


@app.get("/v1/relics/{relic_id}/where-to-get")
def relic_sources(relic_id: str) -> JSONResponse:
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


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=False)
