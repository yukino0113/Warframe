import os
from typing import Any, List, Optional

import requests


class D1Client:
    """Minimal Cloudflare D1 HTTP client for read-only queries.

    Exposes select(query, params) -> List[tuple] returning rows as tuples
    to match sqlite3 cursor.fetchall() shape used by the backend.
    """

    def __init__(self) -> None:
        # Environment loading is handled by callers; but read again just in case.
        self.base_url = os.getenv("D1_PATH")
        self.read_token = os.getenv("D1_READ_TOKEN")
        if not self.base_url:
            raise RuntimeError("D1_PATH is not set")
        if not self.read_token:
            raise RuntimeError("D1_READ_TOKEN is not set")

    def _call(self, sql: str, params: Optional[List[Any]] = None) -> dict:
        headers = {
            "Authorization": f"Bearer {self.read_token}",
            "Content-Type": "application/json",
        }
        payload = {"sql": sql, "params": params or []}
        resp = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # If API returns success flag or errors list, treat non-success as an error to trigger fallback
        if isinstance(data, dict) and (
            ("success" in data and not data.get("success", True))
            or (
                data.get("errors")
                and isinstance(data.get("errors"), list)
                and len(data["errors"]) > 0
            )
        ):
            # Build an informative message
            errs = data.get("errors") or []
            raise RuntimeError(f"D1 query error: {errs}")
        return data

    @staticmethod
    def _rows_to_tuples(data: dict) -> List[tuple]:
        # Try to normalize a few common D1 response shapes into list[tuple]
        res = data.get("result")

        # Shape A (Cloudflare v4 modern): { result: { results: [ { meta:[{name:..}], data:[{col:val}...] } ] } }
        if isinstance(res, dict) and "results" in res:
            results = res["results"]
            if results and isinstance(results, list):
                block = results[0]
                # 1) Newest shape: meta + data (list of dicts)
                if isinstance(block, dict) and ("data" in block or "rows" in block):
                    meta = block.get("meta", [])
                    cols = (
                        [m.get("name") for m in meta if isinstance(m, dict)]
                        if meta
                        else None
                    )
                    # Some variants use "data" (list of dict rows), some use "rows" (list of lists)
                    if "data" in block and isinstance(block["data"], list):
                        data_rows = block["data"]
                        if data_rows:
                            # If columns are known via meta, order by them; otherwise preserve dict order
                            if cols:
                                return [
                                    tuple(r.get(c) for c in cols) for r in data_rows
                                ]
                            else:
                                first_keys = list(data_rows[0].keys())
                                return [
                                    tuple(r.get(c) for c in first_keys)
                                    for r in data_rows
                                ]
                        return []
                    if "rows" in block and isinstance(block["rows"], list):
                        rows = block["rows"]
                        if rows and isinstance(rows[0], list):
                            return [tuple(r) for r in rows]
                        if rows and isinstance(rows[0], dict):
                            # Rare: rows as list of dicts
                            if cols:
                                return [tuple(r.get(c) for c in cols) for r in rows]
                            first_keys = list(rows[0].keys())
                            return [tuple(r.get(c) for c in first_keys) for r in rows]
                        return []
                # 2) Older shape nested under results: { results: [ { results: [ { columns:[...], rows:[[...]] } ] } ] }
                inner = block.get("results") if isinstance(block, dict) else None
                if inner and isinstance(inner, list) and inner:
                    inner_block = inner[0]
                    if isinstance(inner_block, dict):
                        cols = inner_block.get("columns") or [
                            m.get("name")
                            for m in inner_block.get("meta", [])
                            if isinstance(m, dict)
                        ]
                        rows = (
                            inner_block.get("rows")
                            or inner_block.get("values")
                            or inner_block.get("results")
                        )
                        if isinstance(rows, list):
                            if rows and isinstance(rows[0], list):
                                return [tuple(r) for r in rows]
                            if rows and isinstance(rows[0], dict) and cols:
                                return [tuple(r.get(c) for c in cols) for r in rows]
                            return []

        # Shape B (very old): { result: [ { results: [ { columns:[...], rows:[[...]] } ] } ] }
        # Also handle: { result: [ { results: [ {rowdict}, {rowdict}, ... ] } ] }
        if isinstance(res, list) and res:
            first = res[0]
            inner = first.get("results") if isinstance(first, dict) else None
            if inner and isinstance(inner, list):
                # Case B1: inner[0] is a dict with rows/columns (older structured block)
                block = inner[0]
                if isinstance(block, dict) and (
                    "rows" in block or "columns" in block or "values" in block
                ):
                    rows = block.get("rows") or block.get("values")
                    if rows and isinstance(rows, list):
                        return [
                            tuple(r) if isinstance(r, list) else tuple(r.values())
                            for r in rows
                        ]
                # Case B2: inner is directly a list of row dicts
                if inner and isinstance(inner[0], dict):
                    cols = list(inner[0].keys())
                    return [tuple(row.get(c) for c in cols) for row in inner]

        # Shape C: top-level "results" list of dicts
        if "results" in data and isinstance(data["results"], list):
            rows = data["results"]
            if rows and isinstance(rows[0], dict):
                cols = list(rows[0].keys())
                return [tuple(r.get(c) for c in cols) for r in rows]

        # Shape D: { result: { meta:[...], rows:[[...]] } } or { result: { records:[{...}] } }
        if isinstance(res, dict):
            if "rows" in res and isinstance(res["rows"], list):
                rows = res["rows"]
                if rows and isinstance(rows[0], list):
                    return [tuple(r) for r in rows]
            if "records" in res and isinstance(res["records"], list):
                records = res["records"]
                if records and isinstance(records[0], dict):
                    cols = [
                        m.get("name")
                        for m in res.get("meta", [])
                        if isinstance(m, dict)
                    ] or list(records[0].keys())
                    return [tuple(r.get(c) for c in cols) for r in records]

        return []

    def select(self, query: str, params: Optional[List[Any]] = None) -> List[tuple]:
        data = self._call(query, params=params)
        return self._rows_to_tuples(data)
