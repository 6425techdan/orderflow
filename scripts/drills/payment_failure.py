#!/usr/bin/env python3
"""Drill: payment provider failure via payment-mock faults."""

from __future__ import annotations

import time
import uuid

import httpx

API = "http://localhost:8080"
PAY = "http://localhost:8082"


def main() -> int:
    with httpx.Client(timeout=10.0) as client:
        client.post(f"{PAY}/v1/faults", json={"force_fail": True, "fail_rate": 1.0})
        idem = f"drill-payfail-{uuid.uuid4()}"
        resp = client.post(
            f"{API}/v1/orders",
            json={
                "location_id": 7,
                "idempotency_key": idem,
                "items": [{"sku": "burger", "quantity": 1, "unit_price_cents": 500}],
            },
        )
        resp.raise_for_status()
        order_id = resp.json()["order_id"]
        final = None
        for _ in range(20):
            time.sleep(1)
            got = client.get(f"{API}/v1/orders/{order_id}").json()
            final = got["status"]
            if final in {"failed", "dead_lettered", "completed"}:
                break
        client.post(f"{PAY}/v1/faults", json={"force_fail": False, "fail_rate": 0.0})
        print({"order_id": order_id, "final_status": final})
        return 0 if final in {"failed", "dead_lettered"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
