from fastapi.testclient import TestClient

from API_main import app
from backend.encode import encode_bitmap, encode_list

client = TestClient(app)

encode_path = "/encode"


class TestEncodeFunctions:
    def test_encode_bitmap_returns_correct_encoding_for_non_empty_list(self):
        # [1, 2, 3] -> bits 1,2,3 set -> 0b00001110 -> 14 -> b'\x0e' -> 'Dg'
        result = encode_bitmap([1, 2, 3])
        assert result == "BDg"

    def test_encode_bitmap_returns_empty_string_for_empty_list(self):
        result = encode_bitmap([])
        assert result == ""

    def test_encode_list_returns_correct_encoding_for_non_empty_list(self):
        result = encode_list([1, 2, 3])
        assert result == "LMSwyLDM"

    def test_encode_list_returns_correct_encoding_for_empty_list(self):
        result = encode_list([])
        assert result == "L"


class TestEncodeAPI:
    def test_encode_data_returns_bitmap_when_shorter(self):
        # bitmap: "BDg" (len 3), list: "LMSwyLDM" (len 8). Bitmap is shorter.
        response = client.post(encode_path, json={"data": [1, 2, 3]})
        assert response.status_code == 200
        assert response.json()["data"] == "BDg"

    def test_encode_data_returns_list_when_shorter(self):
        # For a sparse list, list encoding is shorter.
        # encode_list([1000]) -> "LMTAwMA" (len 7)
        # encode_bitmap([1000]) -> is much longer.
        response = client.post(encode_path, json={"data": [1000]})
        assert response.status_code == 200
        assert response.json()["data"] == "LMTAwMA"

    def test_encode_data_returns_empty_string_for_empty_list(self):
        response = client.post(encode_path, json={"data": []})
        assert response.status_code == 200
        assert response.json()["data"] == ""
