from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient

# Integration tests require local Postgres + Redis. Skip cleanly when unavailable.
pytestmark = pytest.mark.skipif(
    os.getenv("ORDERFLOW_INTEGRATION", "0") != "1",
    reason="Set ORDERFLOW_INTEGRATION=1 with local Postgres/Redis to run",
)


@pytest.fixture()
def api_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("OTEL_ENABLED", "false")
    from order_api.main import app

    return TestClient(app)


def test_idempotent_order_accept(api_client: TestClient) -> None:
    key = f"itest-{uuid.uuid4()}"
    payload = {
        "location_id": 3,
        "idempotency_key": key,
        "items": [{"sku": "burger", "quantity": 1, "unit_price_cents": 500}],
    }
    first = api_client.post("/v1/orders", json=payload)
    assert first.status_code == 202
    second = api_client.post("/v1/orders", json=payload)
    assert second.status_code == 202
    assert first.json()["order_id"] == second.json()["order_id"]
