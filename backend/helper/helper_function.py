import os
from typing import Optional, List, Dict
import dotenv

dotenv.load_dotenv()

from database.WarframeDB import WarframeDB


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
                      fetchall("SELECT prize FROM mission_rewards WHERE prize LIKE '% %%' GROUP BY prize")}
    relics_bounty = {r[0] for r in fetchall("SELECT prize FROM bounty_rewards WHERE prize LIKE '% %%' GROUP BY prize")}
    relics_dynamic = {r[0] for r in
                      fetchall("SELECT prize FROM dynamic_location_rewards WHERE prize LIKE '% %%' GROUP BY prize")}
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
            f"SELECT relic, prize FROM relic_rewards WHERE relic IN ({qmarks})",
            tuple(available_candidates)
        )
        # For each relic, check if it has a warframe component reward not excluded
        for relic_name, prize in rows:
            if is_excluded(prize, exclude_words):
                continue
            if detect_type(prize) == "warframe_component":
                warframe_relics.add(relic_name)

    return available_candidates & warframe_relics


def get_available_prime() -> List[str]:
    """
    Return a list of Prime set names (e.g., "Wisp Prime") that are currently obtainable
    via relics.
    Uses get_available_relics() to limit to currently available relics.
    """
    available_relics = get_available_relics()
    if not available_relics:
        return []

    # Find rewards from those relics that are Warframe components we care about
    # Use ? ma
    qmarks = ",".join(["?"] * len(available_relics))
    rows = fetchall(
        f"""
        SELECT prize FROM relic_rewards
        WHERE relic IN ({qmarks})
            AND LOWER(prize) LIKE '% prime %'
        """,
        tuple(available_relics)
    )
    suffixes = ["Prime"]
    names: set = set()
    for (prize,) in rows:
        if suffixes in prize.strip():
            names.add(f'{prize.strip().split(suffixes)[0].strip()} Prime')

    return sorted(names)
