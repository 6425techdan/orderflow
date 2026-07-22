#!/usr/bin/env python3
"""Drill: payment provider latency."""

from __future__ import annotations

import time
import uuid

import httpx

API = "http://localhost:8080"
PAY = "http://localhost:8082"


def main() -> int:
    with httpx.Client(timeout=30.0) as client:
        client.post(f"{PAY}/v1/faults", json={"latency_ms": 2000, "force_fail": False, "fail_rate": 0.0})
        start = time.perf_counter()
        resp = client.post(
            f"{API}/v1/orders",
            json={
                "location_id": 8,
                "idempotency_key": f"drill-paylat-{uuid.uuid4()}",
                "items": [{"sku": "fries", "quantity": 1, "unit_price_cents": 299}],
            },
        )
        resp.raise_for_status()
        order_id = resp.json()["order_id"]
        for _ in range(40):
            status = client.get(f"{API}/v1/orders/{order_id}").json()["status"]
            if status in {"completed", "failed", "dead_lettered"}:
                break
            time.sleep(0.5)
        elapsed = time.perf_counter() - start
        client.post(f"{PAY}/v1/faults", json={"latency_ms": 0})
        print({"order_id": order_id, "status": status, "elapsed_s": round(elapsed, 2)})
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
