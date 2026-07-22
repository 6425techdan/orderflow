from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class OrderStatus(str, Enum):
    ACCEPTED = "accepted"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD_LETTERED = "dead_lettered"


class OrderItem(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    quantity: int = Field(ge=1, le=50)
    unit_price_cents: int = Field(ge=0)


class OrderCreate(BaseModel):
    location_id: int = Field(ge=1, le=300, description="Simulated restaurant location 1-300")
    items: list[OrderItem] = Field(min_length=1, max_length=20)
    idempotency_key: str = Field(min_length=8, max_length=128)
    customer_ref: str = Field(default="anon", max_length=64)

    @field_validator("idempotency_key")
    @classmethod
    def strip_key(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("idempotency_key must not be blank")
        return cleaned


class OrderResponse(BaseModel):
    order_id: UUID
    status: OrderStatus
    location_id: int
    idempotency_key: str
    correlation_id: str
    total_cents: int
    created_at: datetime
    updated_at: datetime
    kitchen_station: str | None = None
    failure_reason: str | None = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    checks: dict[str, str] = Field(default_factory=dict)


class PaymentRequest(BaseModel):
    order_id: UUID
    amount_cents: int = Field(ge=0)
    correlation_id: str
    location_id: int


class PaymentResponse(BaseModel):
    payment_id: UUID
    status: str
    latency_ms: int
    provider: str = "payment-mock"


class QueueMessage(BaseModel):
    order_id: str
    location_id: int
    total_cents: int
    correlation_id: str
    idempotency_key: str
    enqueued_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    attempt: int = 0
    items: list[dict[str, Any]] = Field(default_factory=list)
    # W3C traceparent for Redis Streams → worker span linking (optional for older payloads).
    traceparent: str | None = None


def new_order_id() -> UUID:
    return uuid4()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
