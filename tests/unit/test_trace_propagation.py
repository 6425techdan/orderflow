from __future__ import annotations

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from orderflow_common.telemetry import (
    attach_traceparent,
    detach_context,
    inject_traceparent,
    setup_tracing,
)


def test_traceparent_round_trip_links_spans() -> None:
    """API inject → Redis carrier → worker extract should share one trace id."""
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer("test-traceparent")

    with tracer.start_as_current_span("create_order"):
        with tracer.start_as_current_span("enqueue_order"):
            carrier = inject_traceparent()

    assert carrier is not None
    assert carrier.startswith("00-")

    token = attach_traceparent(carrier)
    try:
        with tracer.start_as_current_span("process_order"):
            pass
    finally:
        detach_context(token)

    spans = exporter.get_finished_spans()
    assert len(spans) == 3
    trace_ids = {format(s.context.trace_id, "032x") for s in spans}
    assert len(trace_ids) == 1


def test_attach_none_is_noop() -> None:
    assert attach_traceparent(None) is None
    detach_context(None)


def test_setup_tracing_disabled_noop() -> None:
    setup_tracing("noop-svc", "0.0.0", "http://localhost:4318", enabled=False)
