from __future__ import annotations

import os
import signal
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from uuid import UUID

import httpx
import structlog
from orderflow_common.db import Database
from orderflow_common.kitchen import route_kitchen
from orderflow_common.logging import configure_logging
from orderflow_common.models import OrderStatus, PaymentRequest, QueueMessage
from orderflow_common.queue import OrderQueue
from orderflow_common.resilience import CircuitBreaker, retry_with_backoff
from orderflow_common.settings import CommonSettings
from orderflow_common.telemetry import (
    DB_POOL_AVAILABLE,
    ORDERS_PROCESSED,
    PAYMENT_CALLS,
    PAYMENT_LATENCY,
    QUEUE_AGE,
    QUEUE_DEPTH,
    attach_traceparent,
    detach_context,
    get_tracer,
    inject_traceparent,
    metrics_payload,
    setup_tracing,
)

SERVICE = "order-worker"
settings = CommonSettings(service_name=SERVICE)
configure_logging(SERVICE, settings.log_level)
log = structlog.get_logger()
db = Database(settings.database_url, settings.db_pool_min, settings.db_pool_max)
queue = OrderQueue(settings.redis_url, settings.orders_stream, settings.orders_group, settings.dead_letter_stream)
breaker = CircuitBreaker(failure_threshold=5, reset_timeout=20.0)
_running = True
MAX_ATTEMPTS = 3


def _handle_signal(signum: int, _frame: object) -> None:
    global _running
    log.info("shutdown_signal", signal=signum)
    _running = False


def process_message(message: QueueMessage) -> None:
    order_id = UUID(message.order_id)
    structlog.contextvars.bind_contextvars(correlation_id=message.correlation_id, order_id=message.order_id)
    tracer = get_tracer(SERVICE)
    token = attach_traceparent(message.traceparent)
    try:
        with tracer.start_as_current_span("process_order") as span:
            span.set_attribute("order.id", message.order_id)
            span.set_attribute("location.id", message.location_id)

            db.update_status(order_id, OrderStatus.PROCESSING)
            primary_sku = message.items[0]["sku"] if message.items else "unknown"
            station = route_kitchen(message.location_id, primary_sku)

            if breaker.is_open:
                raise RuntimeError("payment circuit open")

            start = time.perf_counter()
            try:
                with tracer.start_as_current_span("payment_charge"):
                    payment = retry_with_backoff(
                        lambda: _charge(message),
                        attempts=3,
                        base_delay=0.05,
                        retry_on=(httpx.HTTPError, RuntimeError),
                    )
                PAYMENT_CALLS.labels(SERVICE, "success").inc()
                breaker.record_success()
            except Exception:
                PAYMENT_CALLS.labels(SERVICE, "failure").inc()
                breaker.record_failure()
                raise
            finally:
                PAYMENT_LATENCY.labels(SERVICE).observe(time.perf_counter() - start)

            # Idempotency: mark only after successful charge so retries can re-attempt failures.
            if not db.mark_processed(order_id):
                log.info("duplicate_skipped", order_id=message.order_id)
                ORDERS_PROCESSED.labels(SERVICE, "duplicate").inc()
                return

            db.update_status(order_id, OrderStatus.COMPLETED, kitchen_station=station)
            ORDERS_PROCESSED.labels(SERVICE, "completed").inc()
            log.info("order_completed", kitchen_station=station, payment_id=str(payment.get("payment_id")))
    finally:
        detach_context(token)


def _charge(message: QueueMessage) -> dict[str, object]:
    req = PaymentRequest(
        order_id=UUID(message.order_id),
        amount_cents=message.total_cents,
        correlation_id=message.correlation_id,
        location_id=message.location_id,
    )
    with httpx.Client(timeout=2.0) as client:
        url = f"{settings.payment_url.rstrip('/')}/v1/payments"
        resp = client.post(url, json=req.model_dump(mode="json"))
        if resp.status_code >= 500:
            raise RuntimeError(f"payment provider error: {resp.status_code}")
        if resp.status_code >= 400:
            raise RuntimeError(f"payment rejected: {resp.text}")
        return resp.json()


def refresh_gauges() -> None:
    QUEUE_DEPTH.labels(SERVICE).set(queue.stream_length())
    QUEUE_AGE.labels(SERVICE).set(queue.oldest_age_seconds())
    stats = db.pool_stats()
    DB_POOL_AVAILABLE.labels(SERVICE).set(stats.get("pool_available", 0))


class _MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/metrics":
            self.send_response(404)
            self.end_headers()
            return
        payload = metrics_payload()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return


def start_metrics_server(port: int) -> None:
    server = HTTPServer(("0.0.0.0", port), _MetricsHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    log.info("metrics_server_started", port=port)


def main() -> None:
    setup_tracing(
        SERVICE,
        settings.service_version,
        settings.otel_exporter_otlp_endpoint,
        settings.otel_enabled,
    )
    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)
    db.open()
    db.migrate()
    queue.ensure_group()
    start_metrics_server(int(os.getenv("METRICS_PORT", "8081")))
    consumer = os.getenv("WORKER_CONSUMER", f"worker-{uuid.uuid4().hex[:8]}")
    log.info("worker_started", consumer=consumer)

    while _running:
        refresh_gauges()
        batch = queue.read_group(consumer, count=1, block_ms=2000)
        for msg_id, message in batch:
            try:
                if message.attempt >= MAX_ATTEMPTS:
                    queue.dead_letter(message, "max attempts exceeded")
                    db.update_status(
                        UUID(message.order_id),
                        OrderStatus.DEAD_LETTERED,
                        failure_reason="max attempts",
                    )
                    ORDERS_PROCESSED.labels(SERVICE, "dead_lettered").inc()
                    queue.ack(msg_id)
                    continue
                process_message(message)
                queue.ack(msg_id)
            except Exception as exc:
                log.exception("processing_failed", error=str(exc))
                message.attempt += 1
                if message.attempt >= MAX_ATTEMPTS:
                    queue.dead_letter(message, str(exc))
                    db.update_status(
                        UUID(message.order_id),
                        OrderStatus.FAILED,
                        failure_reason=str(exc),
                    )
                    ORDERS_PROCESSED.labels(SERVICE, "failed").inc()
                    queue.ack(msg_id)
                else:
                    # ack and re-enqueue with incremented attempt; refresh trace link
                    queue.ack(msg_id)
                    message.traceparent = inject_traceparent() or message.traceparent
                    queue.enqueue(message)
                    db.update_status(
                        UUID(message.order_id),
                        OrderStatus.QUEUED,
                        failure_reason=str(exc),
                    )

    db.close()
    log.info("worker_stopped")


if __name__ == "__main__":
    main()
