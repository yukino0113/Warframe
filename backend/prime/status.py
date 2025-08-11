from typing import Dict, List, Any
from fastapi.responses import JSONResponse
from fastapi import HTTPException
import json

from API_main import app
from backend.helper.helper_function import fetchall


@app.get("/v1/prime/status")
def get_prime_status() -> JSONResponse:
    """

    :return:
    """

    def components_mapping(text: str):
        return mapping_json[text]

    mapping_json = json.load(open("backend/helper/components.json"))
    rows = fetchall("SELECT name, type, component_type, vaulted FROM prime_set")
    if not rows:
        raise HTTPException(status_code=404, detail="Item not found")

    result: List[Dict[str, Any]] = []
    for name, type_, component_type, vaulted in rows:
        result.append({
            "name": name + ' Prime',
            "type": type_,
            "component_type": components_mapping(component_type),
            "vaulted": vaulted
        })

    return JSONResponse(content=result)
