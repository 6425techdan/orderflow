from __future__ import annotations

import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Header, HTTPException, Request, Response
from fastapi.responses import PlainTextResponse
from orderflow_common.db import Database
from orderflow_common.logging import configure_logging
from orderflow_common.models import (
    HealthResponse,
    OrderCreate,
    OrderResponse,
    OrderStatus,
    QueueMessage,
    new_order_id,
    utcnow,
)
from orderflow_common.queue import OrderQueue
from orderflow_common.settings import CommonSettings
from orderflow_common.telemetry import (
    ORDERS_ACCEPTED,
    QUEUE_DEPTH,
    REQUEST_LATENCY,
    REQUESTS,
    get_tracer,
    inject_traceparent,
    metrics_payload,
    setup_tracing,
)

SERVICE = "order-api"
settings = CommonSettings(service_name=SERVICE)
configure_logging(SERVICE, settings.log_level)
log = structlog.get_logger()
db = Database(settings.database_url, settings.db_pool_min, settings.db_pool_max)
queue = OrderQueue(settings.redis_url, settings.orders_stream, settings.orders_group, settings.dead_letter_stream)
_started = False


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    global _started
    setup_tracing(SERVICE, settings.service_version, settings.otel_exporter_otlp_endpoint, settings.otel_enabled)
    db.open()
    db.migrate()
    queue.ensure_group()
    _started = True
    log.info("service_started", version=settings.service_version)
    yield
    db.close()
    _started = False


app = FastAPI(title="OrderFlow order-api", version=settings.service_version, lifespan=lifespan)


@app.middleware("http")
async def observability_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
    correlation_id = request.headers.get("x-correlation-id") or str(uuid.uuid4())
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
    start = time.perf_counter()
    response: Response = await call_next(request)
    elapsed = time.perf_counter() - start
    route = request.url.path
    REQUESTS.labels(SERVICE, request.method, route, str(response.status_code)).inc()
    REQUEST_LATENCY.labels(SERVICE, route).observe(elapsed)
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Service-Version"] = settings.service_version
    return response


@app.get("/healthz", response_model=HealthResponse)
def healthz() -> HealthResponse:
    return HealthResponse(status="ok", service=SERVICE, version=settings.service_version)


@app.get("/readyz", response_model=HealthResponse)
def readyz() -> HealthResponse:
    checks = {"database": db.health(), "redis": queue.health()}
    status = "ok" if all(v == "ok" for v in checks.values()) else "degraded"
    if status != "ok":
        raise HTTPException(status_code=503, detail=checks)
    return HealthResponse(status=status, service=SERVICE, version=settings.service_version, checks=checks)


@app.get("/startupz", response_model=HealthResponse)
def startupz() -> HealthResponse:
    if not _started:
        raise HTTPException(status_code=503, detail="starting")
    return HealthResponse(status="ok", service=SERVICE, version=settings.service_version)


@app.get("/metrics")
def metrics() -> PlainTextResponse:
    QUEUE_DEPTH.labels(SERVICE).set(queue.stream_length())
    return PlainTextResponse(metrics_payload().decode("utf-8"), media_type="text/plain; version=0.0.4")


@app.post("/v1/orders", response_model=OrderResponse, status_code=202)
def create_order(
    body: OrderCreate,
    x_correlation_id: str | None = Header(default=None),
    x_menu_version: str | None = Header(default=None),
) -> OrderResponse:
    tracer = get_tracer(SERVICE)
    with tracer.start_as_current_span("create_order") as span:
        span.set_attribute("location.id", body.location_id)
        if settings.stale_menu_reject and x_menu_version and x_menu_version != settings.menu_version:
            raise HTTPException(status_code=409, detail="stale menu configuration")

        if settings.fault_db_exhaust:
            raise HTTPException(
                status_code=503,
                detail="database connection pool exhausted (fault injection)",
            )

        existing = db.get_by_idempotency(body.idempotency_key)
        if existing:
            log.info("idempotent_hit", order_id=str(existing.order_id))
            return existing

        correlation_id = x_correlation_id or str(uuid.uuid4())
        total = sum(i.quantity * i.unit_price_cents for i in body.items)
        now = utcnow()
        order = OrderResponse(
            order_id=new_order_id(),
            status=OrderStatus.ACCEPTED,
            location_id=body.location_id,
            idempotency_key=body.idempotency_key,
            correlation_id=correlation_id,
            total_cents=total,
            created_at=now,
            updated_at=now,
        )
        items = [i.model_dump() for i in body.items]
        saved = db.insert_order(order, items)
        with tracer.start_as_current_span("enqueue_order"):
            queue.enqueue(
                QueueMessage(
                    order_id=str(saved.order_id),
                    location_id=saved.location_id,
                    total_cents=saved.total_cents,
                    correlation_id=correlation_id,
                    idempotency_key=saved.idempotency_key,
                    items=items,
                    traceparent=inject_traceparent(),
                )
            )
        db.update_status(saved.order_id, OrderStatus.QUEUED)
        ORDERS_ACCEPTED.labels(SERVICE).inc()
        log.info("order_accepted", order_id=str(saved.order_id), location_id=saved.location_id)
        refreshed = db.get_order(saved.order_id)
        assert refreshed is not None
        span.set_attribute("order.id", str(refreshed.order_id))
        return refreshed


@app.get("/v1/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: uuid.UUID) -> OrderResponse:
    order = db.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="order not found")
    return order


@app.post("/v1/faults")
def set_faults(payload: dict[str, object]) -> dict[str, object]:
    """Lab-only fault injection controls. Not for production use."""
    if "db_exhaust" in payload:
        settings.fault_db_exhaust = bool(payload["db_exhaust"])
    if "stale_menu_reject" in payload:
        settings.stale_menu_reject = bool(payload["stale_menu_reject"])
    if "menu_version" in payload:
        settings.menu_version = str(payload["menu_version"])
    return {
        "fault_db_exhaust": settings.fault_db_exhaust,
        "stale_menu_reject": settings.stale_menu_reject,
        "menu_version": settings.menu_version,
    }
