import base64
from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class GetDecodeRequest(BaseModel):
    data: str


class GetDecodeResponse(BaseModel):
    data: List[int]


def decode_list(s: str) -> List[int]:
    raw = base64.urlsafe_b64decode(s.encode("ascii") + b"=" * (-len(s) % 4))
    if not raw:
        return []
    return list(map(int, raw.decode("ascii").split(",")))


def decode_bitmap(s: str) -> List[int]:
    raw = base64.urlsafe_b64decode(s.encode("ascii") + b"=" * (-len(s) % 4))
    result = []
    for byte_index, byte in enumerate(raw):
        for bit_index in range(8):
            if byte & (1 << bit_index):
                result.append(byte_index * 8 + bit_index)
    return result


@router.post("", response_model=GetDecodeResponse)
def decode_data(req: GetDecodeRequest):
    if not req.data:
        return GetDecodeResponse(data=[])
    if req.data[0] == "B":
        return GetDecodeResponse(data=decode_bitmap(req.data[1:]))
    elif req.data[0] == "L":
        return GetDecodeResponse(data=decode_list(req.data[1:]))
    else:
        raise ValueError("Invalid format")
