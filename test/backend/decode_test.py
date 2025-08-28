from fastapi.testclient import TestClient

from backend.decode import decode_bitmap, decode_list
from backend.main import app

client = TestClient(app)

decode_path = "/decode"


class TestDecodeFunctions:
    def test_decode_list_returns_correct_decoding_for_valid_input(self):
        result = decode_list("MSwyLDM")
        assert result == [1, 2, 3]

    def test_decode_list_returns_empty_list_for_empty_input(self):
        result = decode_list("")
        assert result == []

    def test_decode_bitmap_returns_correct_decoding_for_valid_input(self):
        # "BQA" is decoded from base64 to `b'\x05\x00'`, which has bits 0 and 2 set.
        result = decode_bitmap("BQA")
        assert result == [0, 2]

    def test_decode_bitmap_returns_empty_list_for_empty_input(self):
        result = decode_bitmap("")
        assert result == []


class TestDecodeAPI:
    def test_decode_data_returns_decoded_bitmap_for_bitmap_input(self):
        # The API receives "BQA", strips the "B" and decodes "QA".
        # "QA" is decoded from base64 to `b'@'` (64), which has only bit 6 set.
        response = client.post(decode_path, json={"data": "BQA"})
        assert response.status_code == 200
        assert response.json()["data"] == [6]

    def test_decode_data_returns_decoded_list_for_list_input(self):
        response = client.post(decode_path, json={"data": "LMSwyLDM"})
        assert response.status_code == 200
        assert response.json()["data"] == [1, 2, 3]

    def test_decode_data_returns_empty_list_for_empty_input(self):
        response = client.post(decode_path, json={"data": ""})
        assert response.status_code == 200
        assert response.json()["data"] == []

    def test_decode_data_raises_error_for_invalid_format(self):
        response = client.post(decode_path, json={"data": "X123"})
        assert response.status_code == 400
