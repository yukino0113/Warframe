import base64
import math
from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class GetEncodeRequest(BaseModel):
    data: List[int]


class GetEncodeResponse(BaseModel):
    data: str


def encode_bitmap(int_arr: List[int]) -> str:
    if not int_arr:
        return ""
    if any(num < 0 for num in int_arr):
        raise ValueError("All numbers must be non-negative")
    max_val = max(int_arr)
    bit_len = max_val + 1
    byte_len = math.ceil(bit_len / 8)
    bit_array = bytearray(byte_len)

    for num in int_arr:
        byte_index = num // 8
        bit_index = num % 8
        bit_array[byte_index] |= (1 << bit_index)

    return "B" + base64.urlsafe_b64encode(bit_array).decode("ascii").rstrip("=")


def encode_list(int_arr: List[int]) -> str:
    joined = ",".join(map(str, int_arr))
    return "L" + base64.urlsafe_b64encode(joined.encode("ascii")).decode("ascii").rstrip("=")


@router.post("", response_model=GetEncodeResponse)
def encode_data(req: GetEncodeRequest):
    arr = sorted(set(req.data))  # 去重 + 排序
    b64_bitmap = encode_bitmap(arr)
    b64_list = encode_list(arr)

    # 選最短的方案
    if len(b64_list) < len(b64_bitmap):
        return GetEncodeResponse(data=b64_list)
    else:
        return GetEncodeResponse(data=b64_bitmap)
