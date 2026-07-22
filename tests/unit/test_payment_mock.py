from __future__ import annotations

from fastapi.testclient import TestClient

# Import after path setup via pytest pythonpath
from payment_mock.main import _state, app


def test_payment_mock_success() -> None:
    _state["latency_ms"] = 0
    _state["fail_rate"] = 0.0
    _state["force_fail"] = False
    client = TestClient(app)
    resp = client.post(
        "/v1/payments",
        json={
            "order_id": "11111111-1111-1111-1111-111111111111",
            "amount_cents": 1000,
            "correlation_id": "c-1",
            "location_id": 1,
        },
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "captured"


def test_payment_mock_force_fail() -> None:
    client = TestClient(app)
    client.post("/v1/faults", json={"force_fail": True})
    resp = client.post(
        "/v1/payments",
        json={
            "order_id": "22222222-2222-2222-2222-222222222222",
            "amount_cents": 1000,
            "correlation_id": "c-2",
            "location_id": 2,
        },
    )
    assert resp.status_code == 502
    client.post("/v1/faults", json={"force_fail": False})
