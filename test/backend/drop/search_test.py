import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


class TestDropSearchAPI:
    search_url = "/drop/search"
    fetchall_attr = "backend.drop.search.fetchall"
    get_available_sets_attr = "backend.drop.search.get_available_sets"

    mock_prime_parts = [
        ("Set1", "PartA"),
        ("Set2", "PartB"),
    ]
    mock_relic_rewards = [
        ("Set1 Prime PartA", "Radiant", 0.1, "Relic1"),
        ("Set2 Prime PartB", "Intact", 0.2, "Relic2"),
    ]
    mock_reward_tables = [
        ("Relic1", 0.5, "Source1", "Rotation A"),
        ("Relic2", 0.3, "Source2", "Rotation B"),
    ]

    def test_search_drop_success(self, monkeypatch):
        def mock_fetchall(query, params=None):
            if "prime_parts" in query:
                return self.mock_prime_parts
            if "relic_rewards" in query:
                return self.mock_relic_rewards
            # This will be called for each table in RewardTables.TABLES
            # We can simplify by returning the same data for all.
            return self.mock_reward_tables

        monkeypatch.setattr(self.fetchall_attr, mock_fetchall)
        monkeypatch.setattr(self.get_available_sets_attr, lambda: ["Set1", "Set2"])

        response = client.post(self.search_url, json={"data": [1, 2]})

        assert response.status_code == 200
        data = response.json()

        assert "relic_score" in data
        assert "area_score" in data

        assert "Relic1" in data["relic_score"]
        assert data["relic_score"]["Relic1"]["score"] == pytest.approx(0.1)
        assert "Set1 Prime PartA" in data["relic_score"]["Relic1"]["item_list"]

        assert "Source1" in data["area_score"]
        assert data["area_score"]["Source1"]["score"] > 0

    def test_search_drop_empty_input(self):
        response = client.post(self.search_url, json={"data": []})
        assert response.status_code == 200
        data = response.json()
        assert data == {"relic_score": {}, "area_score": {}}

    def test_search_drop_no_results(self, monkeypatch):
        monkeypatch.setattr(self.fetchall_attr, lambda *args, **kwargs: [])
        monkeypatch.setattr(self.get_available_sets_attr, lambda: [])

        response = client.post(self.search_url, json={"data": [1, 2]})
        assert response.status_code == 200
        data = response.json()
        assert data == {"relic_score": {}, "area_score": {}}

    def test_search_drop_server_error(self, monkeypatch):
        def raise_exception(*args, **kwargs):
            raise ConnectionError("Database error")

        monkeypatch.setattr(self.fetchall_attr, raise_exception)
        monkeypatch.setattr(self.get_available_sets_attr, lambda: ["Set1"])

        response = client.post(self.search_url, json={"data": [1]})
        assert response.status_code == 400  # The API returns 400 for any exception
