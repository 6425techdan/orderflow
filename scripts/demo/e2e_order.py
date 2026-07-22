#!/usr/bin/env python3
"""End-to-end order demonstration against local Compose stack."""

from __future__ import annotations

import sys
import time
import uuid

import httpx

API = "http://localhost:8080"


def main() -> int:
    idem = f"demo-{uuid.uuid4()}"
    payload = {
        "location_id": 101,
        "idempotency_key": idem,
        "items": [{"sku": "burger", "quantity": 1, "unit_price_cents": 799}],
        "customer_ref": "lab-demo",
    }
    with httpx.Client(timeout=10.0) as client:
        for _ in range(30):
            try:
                if client.get(f"{API}/readyz").status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            time.sleep(2)
        else:
            print("API not ready", file=sys.stderr)
            return 1

        create = client.post(f"{API}/v1/orders", json=payload, headers={"X-Correlation-ID": "demo-e2e"})
        create.raise_for_status()
        order = create.json()
        order_id = order["order_id"]
        print("accepted", order_id, order["status"])

        # idempotent replay
        replay = client.post(f"{API}/v1/orders", json=payload)
        replay.raise_for_status()
        assert replay.json()["order_id"] == order_id

        for _ in range(30):
            got = client.get(f"{API}/v1/orders/{order_id}")
            got.raise_for_status()
            status = got.json()["status"]
            print("status", status)
            if status in {"completed", "failed", "dead_lettered"}:
                print(got.json())
                return 0 if status == "completed" else 2
            time.sleep(1)
        print("timeout waiting for completion", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
