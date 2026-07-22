#!/usr/bin/env python3
"""Drill: API database connection exhaustion fault."""

from __future__ import annotations

import httpx

API = "http://localhost:8080"


def main() -> int:
    with httpx.Client(timeout=10.0) as client:
        client.post(f"{API}/v1/faults", json={"db_exhaust": True})
        resp = client.post(
            f"{API}/v1/orders",
            json={
                "location_id": 9,
                "idempotency_key": "drill-db-exhaust-0001",
                "items": [{"sku": "soda", "quantity": 1, "unit_price_cents": 199}],
            },
        )
        client.post(f"{API}/v1/faults", json={"db_exhaust": False})
        print({"status_code": resp.status_code, "body": resp.text})
        return 0 if resp.status_code == 503 else 1


if __name__ == "__main__":
    raise SystemExit(main())
