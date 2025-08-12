from fastapi.testclient import TestClient

from API_main import app

client = TestClient(app)
prime_status_url = "/v1/prime/status"
attr = "backend.helper.helper_function.fetchall"


def get_prime_status_returns_data_when_vault_has_sets():
    response = client.get(prime_status_url)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    for prime_set in response.json():
        assert "warframe_set" in prime_set
        assert "status" in prime_set
        assert "type" in prime_set
        assert "parts" in prime_set
        assert isinstance(prime_set["parts"], list)


def get_prime_status_returns_404_when_no_sets_in_vault(monkeypatch):
    monkeypatch.setattr(attr, lambda query: [])
    response = client.get(prime_status_url)
    assert response.status_code == 404
    assert response.json()["detail"] == "No Prime sets found in the vault status"


def get_prime_status_skips_sets_with_no_parts(monkeypatch):
    monkeypatch.setattr(attr, lambda query, params=None: [])
    response = client.get(prime_status_url)
    assert response.status_code == 404
    assert response.json()["detail"] == "No Prime sets found in the database."


def get_prime_status_handles_server_error_gracefully(monkeypatch):
    def raise_exception():
        raise ConnectionError("Database error")

    monkeypatch.setattr(attr, lambda query, params=None: raise_exception())
    response = client.get(prime_status_url)
    assert response.status_code == 500
    assert response.json()["detail"] == "Server error while fetching Prime status data."
