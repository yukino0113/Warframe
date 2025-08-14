from fastapi.testclient import TestClient

from backend.encode import encode_bitmap, encode_list, router

client = TestClient(router)


def encode_bitmap_returns_correct_encoding_for_non_empty_list():
    result = encode_bitmap([1, 2, 3])
    assert result == "BQA"


def encode_bitmap_returns_empty_string_for_empty_list():
    result = encode_bitmap([])
    assert result == ""


def encode_list_returns_correct_encoding_for_non_empty_list():
    result = encode_list([1, 2, 3])
    assert result == "LMSwyLDM"


def encode_list_returns_correct_encoding_for_empty_list():
    result = encode_list([])
    assert result == "L"


def encode_data_returns_shortest_encoding_for_non_empty_list():
    response = client.post("/", json={"data": [1, 2, 3]})
    assert response.status_code == 200
    assert response.json()["data"] == "BQA"


def encode_data_returns_empty_string_for_empty_list():
    response = client.post("/", json={"data": []})
    assert response.status_code == 200
    assert response.json()["data"] == ""
