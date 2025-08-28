from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


class TestPrimeStatusAPI:
    prime_status_url = "/prime/status"
    fetchall_attr = "backend.prime.status.fetchall"

    mock_vault_status = [
        ("Set1", "Available", "Warframe"),
        ("Set2", "Vaulted", "Weapon"),
    ]
    mock_parts_data = {"Set1": [(1, "PartA"), (2, "PartB")], "Set2": [(3, "PartC")]}

    def test_get_prime_status_returns_data_successfully(self, monkeypatch):
        def mock_fetchall(query, params=None):
            if "vault_status" in query:
                return self.mock_vault_status
            if "prime_parts" in query:
                warframe_set = params[0]
                return self.mock_parts_data.get(warframe_set, [])
            return []

        monkeypatch.setattr(self.fetchall_attr, mock_fetchall)
        response = client.get(self.prime_status_url)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

        assert data[0]["warframe_set"] == "Set1"
        assert data[0]["status"] == "Available"
        assert data[0]["type"] == "Warframe"
        assert len(data[0]["parts"]) == 2
        assert data[0]["parts"][0] == {"parts": "PartA", "id": 1}

        assert data[1]["warframe_set"] == "Set2"
        assert data[1]["status"] == "Vaulted"
        assert data[1]["type"] == "Weapon"
        assert len(data[1]["parts"]) == 1
        assert data[1]["parts"][0] == {"parts": "PartC", "id": 3}

    def test_get_prime_status_returns_404_when_no_sets_in_vault(self, monkeypatch):
        monkeypatch.setattr(self.fetchall_attr, lambda *args, **kwargs: [])
        response = client.get(self.prime_status_url)
        assert response.status_code == 404
        assert response.json()["detail"] == "No Prime sets found in the vault status"

    def test_get_prime_status_404_when_all_sets_have_no_parts(self, monkeypatch):
        def mock_fetchall(query, params=None):
            if "vault_status" in query:
                return self.mock_vault_status
            if "prime_parts" in query:
                return []  # No parts for any set
            return []

        monkeypatch.setattr(self.fetchall_attr, mock_fetchall)
        response = client.get(self.prime_status_url)
        assert response.status_code == 404
        assert response.json()["detail"] == "No Prime sets found in the database."

    def test_get_prime_status_handles_server_error(self, monkeypatch):
        def raise_exception(*args, **kwargs):
            raise ConnectionError("Database error")

        monkeypatch.setattr(self.fetchall_attr, raise_exception)
        response = client.get(self.prime_status_url)
        assert response.status_code == 500
        assert (
            response.json()["detail"]
            == "Server error while fetching Prime status data."
        )
