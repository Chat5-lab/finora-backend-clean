from fastapi.testclient import TestClient
from datetime import date
from main import app

c = TestClient(app)

def login():
    r = c.post("/auth/login", data={"username":"owner@example.com","password":"demo123"})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]

def test_accounts_and_post_journal():
    token = login()
    r = c.get("/ledger/accounts", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.text
    accounts = r.json()
    assert accounts, "expected seeded accounts"
    by_code = {a["code"]: a for a in accounts}
    assert "1000" in by_code and "5000" in by_code

    payload = {
        "date": date.today().isoformat(),
        "memo": "Test expense",
        "lines": [
            {"account_id": by_code["5000"]["id"], "debit": 10},
            {"account_id": by_code["1000"]["id"], "credit": 10}
        ]
    }
    r = c.post("/ledger/journals", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 201, r.text

    payload["lines"][0]["debit"] = 11
    r = c.post("/ledger/journals", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 400
