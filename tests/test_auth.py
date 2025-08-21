from fastapi.testclient import TestClient
from main import app

c = TestClient(app)

def test_login_and_me():
    # login with seeded user
    r = c.post("/auth/login", data={"username":"owner@example.com","password":"demo123"})
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    r = c.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "owner@example.com"
