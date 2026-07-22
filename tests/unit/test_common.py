from __future__ import annotations

from orderflow_common.kitchen import route_kitchen
from orderflow_common.models import OrderCreate, OrderItem
from orderflow_common.resilience import CircuitBreaker


def test_kitchen_routing_is_deterministic() -> None:
    assert route_kitchen(12, "burger") == route_kitchen(12, "burger")
    assert route_kitchen(1, "fries") in {"grill", "fry", "assembly", "beverage", "dessert"}


def test_order_create_validation() -> None:
    order = OrderCreate(
        location_id=42,
        idempotency_key="idem-12345678",
        items=[OrderItem(sku="burger", quantity=2, unit_price_cents=499)],
    )
    assert order.location_id == 42


def test_circuit_breaker_opens() -> None:
    breaker = CircuitBreaker(failure_threshold=2, reset_timeout=60)
    breaker.record_failure()
    assert not breaker.is_open
    breaker.record_failure()
    assert breaker.is_open
