from __future__ import annotations

STATIONS = ("grill", "fry", "assembly", "beverage", "dessert")


def route_kitchen(location_id: int, sku: str) -> str:
    """Deterministic kitchen station routing for simulated restaurants."""
    idx = (location_id + sum(ord(c) for c in sku)) % len(STATIONS)
    return STATIONS[idx]
