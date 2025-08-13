import logging
from typing import Dict, List, Any

from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

from backend.helper.helper_function import fetchall


class PrimeStatusService:
    """Get Prime status and parts information from the database."""

    @staticmethod
    def get_vault_status() -> List[tuple]:
        """Fetch all Prime sets and their status from the vault_status table."""
        return fetchall("SELECT warframe_set, status, set_type FROM vault_status ORDER BY warframe_set ")

    @staticmethod
    def get_prime_parts(warframe_set: str) -> List[tuple]:
        """Fetch all Prime parts for a given Prime set."""
        return fetchall(
            "SELECT id, parts_name FROM prime_parts WHERE warframe_set = ? ORDER BY parts_name ,id ",
            (warframe_set,)
        )

    @staticmethod
    def build_prime_set_data(warframe_set: str, status: str, set_type: str, parts_data: List[tuple]) -> Dict[str, Any]:
        """Create a Prime set data object with the given information."""
        return {
            'warframe_set': warframe_set,
            'status': status,
            'type': set_type,
            'parts': [
                {
                    'parts': parts_name,
                    'id': part_id
                }
                for part_id, parts_name in parts_data
            ]
        }


@router.get("")
def get_prime_status() -> JSONResponse:
    """
    Get all prime set data include：
    - Set name
    - Vault status
    - Type（warframe、weapon、companion）
    - Prime parts information (parts name and id))
    
    :return: JSONResponse: Prime set data list
    """
    try:
        service = PrimeStatusService()

        # Fetching Prime status data from the database
        vault_rows = service.get_vault_status()
        if not vault_rows:
            raise HTTPException(status_code=404, detail="No Prime sets found in the vault status")

        result: List[Dict[str, Any]] = []

        # Process each Prime set
        for warframe_set, status, set_type in vault_rows:
            try:
                # Fetch Prime parts for the current set
                parts_data = service.get_prime_parts(warframe_set)

                if not parts_data:
                    logging.warning(f"Sets: {warframe_set} has no Prime parts. Skipping.")
                    continue

                # Create the Prime set data object
                prime_set = service.build_prime_set_data(warframe_set, status, set_type, parts_data)
                result.append(prime_set)

            except Exception as e:
                logging.error(f"ERROR processing Prime set '{warframe_set}': {str(e)}")
                continue

        if not result:
            raise HTTPException(status_code=404, detail="No Prime sets found in the database.")

        return JSONResponse(content=result, media_type="application/json")

    except HTTPException:
        raise
    except Exception as e:
        logging.error("ERROR while fetching Prime status data", exc_info=True)
        raise HTTPException(status_code=500, detail="Server error while fetching Prime status data.") from e
