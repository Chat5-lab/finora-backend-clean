from fastapi.testclient import TestClient
from main import app

c = TestClient(app)

def _auth_headers():
    r = c.post("/auth/login", data={"username": "owner@example.com", "password": "demo123"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}

def test_bank_providers_and_accounts():
    h = _auth_headers()
    r = c.get("/bank/providers", headers=h)
    assert r.status_code == 200, r.text
    providers = r.json()
    assert isinstance(providers, list)

    r = c.get("/bank/accounts", headers=h)
    assert r.status_code in (200, 204), r.text
    if r.status_code == 200:
        assert isinstance(r.json(), list)

def test_bank_oauth_start_stub():
    h = _auth_headers()
    # use whatever provider_id your stub expects; "demo" is typical
    r = c.post("/bank/oauth/start", headers=h, json={"provider_id": "demo"})
    assert r.status_code in (200, 201), r.text
    body = r.json()
    # tolerate different key names used in stubs
    assert any(k in body for k in ("auth_url", "authorize_url", "url"))

def test_bank_sync_stub():
    h = _auth_headers()
    r = c.post("/bank/transactions:sync", headers=h, json={"since": None})
    assert r.status_code == 200, r.text
    body = r.json()
    assert "synced" in body
