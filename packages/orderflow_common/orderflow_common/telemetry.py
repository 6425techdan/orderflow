from __future__ import annotations

import os
from typing import Any

from opentelemetry import context, trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from prometheus_client import Counter, Gauge, Histogram, generate_latest

_TRACE_PROPAGATOR = TraceContextTextMapPropagator()

REQUESTS = Counter(
    "orderflow_http_requests_total",
    "HTTP requests",
    ["service", "method", "route", "status"],
)
REQUEST_LATENCY = Histogram(
    "orderflow_http_request_duration_seconds",
    "HTTP request latency",
    ["service", "route"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5),
)
ORDERS_ACCEPTED = Counter("orderflow_orders_accepted_total", "Orders accepted", ["service"])
ORDERS_PROCESSED = Counter(
    "orderflow_orders_processed_total",
    "Orders processed",
    ["service", "result"],
)
QUEUE_AGE = Gauge("orderflow_queue_age_seconds", "Approximate oldest queue age", ["service"])
QUEUE_DEPTH = Gauge("orderflow_queue_depth", "Stream depth", ["service"])
DB_POOL_AVAILABLE = Gauge("orderflow_db_pool_available", "DB pool available connections", ["service"])
PAYMENT_CALLS = Counter(
    "orderflow_payment_calls_total",
    "Payment dependency calls",
    ["service", "result"],
)
PAYMENT_LATENCY = Histogram(
    "orderflow_payment_latency_seconds",
    "Payment dependency latency",
    ["service"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
)
AI_CALLS = Counter(
    "orderflow_ai_calls_total",
    "AI assistant calls",
    ["service", "mode", "result"],
)
AI_LATENCY = Histogram(
    "orderflow_ai_latency_seconds",
    "AI assistant latency",
    ["service", "mode"],
)
AI_ESTIMATED_COST = Counter(
    "orderflow_ai_estimated_cost_usd_total",
    "Estimated AI cost USD",
    ["service"],
)


def setup_tracing(service_name: str, version: str, endpoint: str, enabled: bool = True) -> None:
    if not enabled:
        return
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": version,
            "deployment.environment": os.getenv("DEPLOY_ENV", "local"),
        }
    )
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=f"{endpoint.rstrip('/')}/v1/traces")
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)


def get_tracer(name: str) -> Any:
    return trace.get_tracer(name)


def inject_traceparent() -> str | None:
    """Serialize current span context as a W3C traceparent header value."""
    carrier: dict[str, str] = {}
    _TRACE_PROPAGATOR.inject(carrier, context=context.get_current())
    return carrier.get("traceparent")


def attach_traceparent(traceparent: str | None) -> Any:
    """Return an OTel context token attaching parent from a W3C traceparent (or None)."""
    if not traceparent:
        return None
    ctx = _TRACE_PROPAGATOR.extract({"traceparent": traceparent})
    return context.attach(ctx)


def detach_context(token: Any) -> None:
    if token is not None:
        context.detach(token)


def metrics_payload() -> bytes:
    return generate_latest()
