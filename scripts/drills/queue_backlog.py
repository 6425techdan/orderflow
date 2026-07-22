#!/usr/bin/env python3
"""Drill: generate queue backlog by pausing payment (slow) and flooding orders."""

from __future__ import annotations

import uuid

import httpx

API = "http://localhost:8080"
PAY = "http://localhost:8082"


def main() -> int:
    with httpx.Client(timeout=10.0) as client:
        client.post(f"{PAY}/v1/faults", json={"latency_ms": 5000})
        accepted = 0
        for i in range(25):
            resp = client.post(
                f"{API}/v1/orders",
                json={
                    "location_id": 1 + (i % 300),
                    "idempotency_key": f"drill-backlog-{uuid.uuid4()}",
                    "items": [{"sku": "burger", "quantity": 1, "unit_price_cents": 799}],
                },
            )
            if resp.status_code in (200, 202):
                accepted += 1
        depth = None
        try:
            metrics = client.get(f"{API}/metrics").text
            for line in metrics.splitlines():
                if line.startswith("orderflow_queue_depth{"):
                    depth = line.split()[-1]
                    break
        except Exception:
            pass
        client.post(f"{PAY}/v1/faults", json={"latency_ms": 0})
        print({"accepted": accepted, "queue_depth_sample": depth})
        return 0 if accepted >= 20 else 1


if __name__ == "__main__":
    raise SystemExit(main())
