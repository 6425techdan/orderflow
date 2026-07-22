#!/usr/bin/env python3
"""Drill: stale menu configuration rejection."""

from __future__ import annotations

import httpx

API = "http://localhost:8080"


def main() -> int:
    with httpx.Client(timeout=10.0) as client:
        client.post(f"{API}/v1/faults", json={"stale_menu_reject": True, "menu_version": "2026.07.01"})
        resp = client.post(
            f"{API}/v1/orders",
            headers={"X-Menu-Version": "2025.01.01"},
            json={
                "location_id": 11,
                "idempotency_key": "drill-stale-menu-0001",
                "items": [{"sku": "burger", "quantity": 1, "unit_price_cents": 799}],
            },
        )
        client.post(f"{API}/v1/faults", json={"stale_menu_reject": False})
        print({"status_code": resp.status_code, "body": resp.text})
        return 0 if resp.status_code == 409 else 1


if __name__ == "__main__":
    raise SystemExit(main())
