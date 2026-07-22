from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any
from uuid import UUID

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from orderflow_common.models import OrderResponse, OrderStatus, utcnow

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS orders (
    order_id UUID PRIMARY KEY,
    location_id INT NOT NULL,
    idempotency_key TEXT NOT NULL UNIQUE,
    correlation_id TEXT NOT NULL,
    status TEXT NOT NULL,
    total_cents INT NOT NULL,
    items JSONB NOT NULL DEFAULT '[]'::jsonb,
    kitchen_station TEXT,
    failure_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS processed_messages (
    order_id UUID PRIMARY KEY,
    processed_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_location ON orders(location_id);
"""


class Database:
    def __init__(self, dsn: str, min_size: int = 1, max_size: int = 10) -> None:
        self._pool = ConnectionPool(
            conninfo=dsn,
            min_size=min_size,
            max_size=max_size,
            kwargs={"row_factory": dict_row},
            open=False,
        )
        self._opened = False

    def open(self) -> None:
        if not self._opened:
            self._pool.open()
            self._opened = True

    def close(self) -> None:
        if self._opened:
            self._pool.close()
            self._opened = False

    def migrate(self) -> None:
        with self.connection() as conn:
            conn.execute(SCHEMA_SQL)
            conn.commit()

    @contextmanager
    def connection(self) -> Iterator[Any]:
        self.open()
        with self._pool.connection() as conn:
            yield conn

    def health(self) -> str:
        try:
            with self.connection() as conn:
                conn.execute("SELECT 1")
            return "ok"
        except Exception:
            return "error"

    def pool_stats(self) -> dict[str, int]:
        stats = self._pool.get_stats()
        return {
            "pool_min": int(stats.get("pool_min", 0)),
            "pool_max": int(stats.get("pool_max", 0)),
            "pool_size": int(stats.get("pool_size", 0)),
            "pool_available": int(stats.get("pool_available", 0)),
        }

    def get_by_idempotency(self, key: str) -> OrderResponse | None:
        with self.connection() as conn:
            row = conn.execute(
                "SELECT * FROM orders WHERE idempotency_key = %s",
                (key,),
            ).fetchone()
        return _row_to_order(row) if row else None

    def get_order(self, order_id: UUID) -> OrderResponse | None:
        with self.connection() as conn:
            row = conn.execute("SELECT * FROM orders WHERE order_id = %s", (str(order_id),)).fetchone()
        return _row_to_order(row) if row else None

    def insert_order(self, order: OrderResponse, items: list[dict[str, Any]]) -> OrderResponse:
        with self.connection() as conn:
            conn.execute(
                """
                INSERT INTO orders (
                    order_id, location_id, idempotency_key, correlation_id, status,
                    total_cents, items, kitchen_station, failure_reason, created_at, updated_at
                ) VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s,%s)
                ON CONFLICT (idempotency_key) DO NOTHING
                """,
                (
                    str(order.order_id),
                    order.location_id,
                    order.idempotency_key,
                    order.correlation_id,
                    order.status.value,
                    order.total_cents,
                    _json(items),
                    order.kitchen_station,
                    order.failure_reason,
                    order.created_at,
                    order.updated_at,
                ),
            )
            conn.commit()
        existing = self.get_by_idempotency(order.idempotency_key)
        assert existing is not None
        return existing

    def update_status(
        self,
        order_id: UUID,
        status: OrderStatus,
        *,
        kitchen_station: str | None = None,
        failure_reason: str | None = None,
    ) -> None:
        with self.connection() as conn:
            conn.execute(
                """
                UPDATE orders
                SET status = %s,
                    kitchen_station = COALESCE(%s, kitchen_station),
                    failure_reason = %s,
                    updated_at = %s
                WHERE order_id = %s
                """,
                (status.value, kitchen_station, failure_reason, utcnow(), str(order_id)),
            )
            conn.commit()

    def mark_processed(self, order_id: UUID) -> bool:
        """Return True if newly processed, False if duplicate."""
        with self.connection() as conn:
            row = conn.execute(
                """
                INSERT INTO processed_messages (order_id, processed_at)
                VALUES (%s, %s)
                ON CONFLICT (order_id) DO NOTHING
                RETURNING order_id
                """,
                (str(order_id), utcnow()),
            ).fetchone()
            conn.commit()
        return row is not None


def _row_to_order(row: dict[str, Any]) -> OrderResponse:
    return OrderResponse(
        order_id=row["order_id"],
        status=OrderStatus(row["status"]),
        location_id=row["location_id"],
        idempotency_key=row["idempotency_key"],
        correlation_id=row["correlation_id"],
        total_cents=row["total_cents"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        kitchen_station=row.get("kitchen_station"),
        failure_reason=row.get("failure_reason"),
    )


def _json(items: list[dict[str, Any]]) -> str:
    import json

    return json.dumps(items)
