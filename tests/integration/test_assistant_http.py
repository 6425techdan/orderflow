from __future__ import annotations

from fastapi.testclient import TestClient
from incident_assistant.main import app


def test_assistant_analyze_fixture() -> None:
    client = TestClient(app)
    resp = client.post(
        "/v1/analyze",
        json={
            "incident_id": "it-1",
            "alerts": [{"name": "PaymentDependencyFailure", "summary": "payment down"}],
            "telemetry_summary": {"payment_success_ratio": 0.2},
            "deployment": {"version": "0.1.0"},
            "runbook_excerpts": ["Check payment-mock"],
            "mode": "fixture",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["hypotheses"][0]["root_cause_id"] == "payment_provider_failure"
    assert body["refused_actions"]
