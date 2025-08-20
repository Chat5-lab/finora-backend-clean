from fastapi.testclient import TestClient
from datetime import date, timedelta
from main import app

c = TestClient(app)

def test_vat_preview_smoke():
    # login with seeded user
    r = c.post("/auth/login", data={"username":"owner@example.com","password":"demo123"})
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]

    today = date.today()
    start = (today.replace(day=1))
    end = today

    r = c.post("/vat/preview",
               headers={"Authorization": f"Bearer {token}"},
               json={"period_start": start.isoformat(), "period_end": end.isoformat()})
    assert r.status_code == 200, r.text
    data = r.json()
    boxes = data.get("boxes", {})
    # Expect box1..box9 present and numeric
    for i in range(1, 10):
        assert f"box{i}" in boxes
        assert isinstance(boxes[f"box{i}"], (int, float))
