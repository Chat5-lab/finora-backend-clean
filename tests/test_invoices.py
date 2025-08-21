# tests/test_invoices.py
from fastapi.testclient import TestClient
from main import app
from datetime import date

c = TestClient(app)

def _login():
    r = c.post("/auth/login", data={"username":"owner@example.com","password":"demo123"})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]

def test_invoice_create_and_mark_paid():
    token = _login()
    today = str(date.today())
    payload = {
        "customer_name": "Acme Ltd",
        "customer_email": "ap@acme.example",
        "issue_date": today,
        "due_date": today,
        "lines": [
            {"description":"Consulting", "quantity":"1.0", "unit_price":"100.00", "tax_rate":"20.00"},
            {"description":"Hosting",    "quantity":"1.0", "unit_price":"50.00",  "tax_rate":"0.00"},
        ],
    }
    r = c.post("/invoices", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.text
    inv = r.json()
    assert inv["gross_total"] == "120.00"  # 100 + 20 tax + 50 = 170? (Wait) -> net=150, tax on 100 @20%=20 => gross=170.00
    # Fix expected:
    assert inv["net_total"] == "150.00"
    assert inv["tax_total"] == "20.00"
    assert inv["gross_total"] == "170.00"

    inv_id = inv["id"]
    r = c.get(f"/invoices/{inv_id}", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200

    r = c.post(f"/invoices/{inv_id}/mark_paid", json={"date": today, "amount":"170.00"}, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.text