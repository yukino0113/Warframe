from fastapi.testclient import TestClient

from backend.decode import decode_bitmap, decode_list, router

client = TestClient(router)


def decode_list_returns_correct_decoding_for_valid_input():
    result = decode_list("MSwyLDM")
    assert result == [1, 2, 3]


def decode_list_returns_empty_list_for_empty_input():
    result = decode_list("")
    assert result == []


def decode_bitmap_returns_correct_decoding_for_valid_input():
    result = decode_bitmap("BQA")
    assert result == [0, 10]


def decode_bitmap_returns_empty_list_for_empty_input():
    result = decode_bitmap("")
    assert result == []


def decode_data_returns_decoded_bitmap_for_bitmap_input():
    response = client.post("/", json={"data": "BQA"})
    assert response.status_code == 200
    assert response.json()["data"] == [0, 10]


def decode_data_returns_decoded_list_for_list_input():
    response = client.post("/", json={"data": "LMSwyLDM"})
    assert response.status_code == 200
    assert response.json()["data"] == [1, 2, 3]


def decode_data_returns_empty_list_for_empty_input():
    response = client.post("/", json={"data": ""})
    assert response.status_code == 200
    assert response.json()["data"] == []


def decode_data_raises_error_for_invalid_format():
    response = client.post("/", json={"data": "X123"})
    assert response.status_code == 422
