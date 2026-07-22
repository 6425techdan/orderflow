from __future__ import annotations

import random
import time
import uuid
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import PlainTextResponse
from orderflow_common.logging import configure_logging
from orderflow_common.models import HealthResponse, PaymentRequest, PaymentResponse
from orderflow_common.settings import CommonSettings
from orderflow_common.telemetry import metrics_payload
from pydantic import BaseModel, Field

SERVICE = "payment-mock"
settings = CommonSettings(service_name=SERVICE)
configure_logging(SERVICE, settings.log_level)

app = FastAPI(title="OrderFlow payment-mock", version=settings.service_version)

_state: dict[str, Any] = {
    "latency_ms": settings.fault_payment_latency_ms,
    "fail_rate": settings.fault_payment_fail_rate,
    "force_fail": False,
}


class FaultConfig(BaseModel):
    latency_ms: int | None = Field(default=None, ge=0, le=30000)
    fail_rate: float | None = Field(default=None, ge=0.0, le=1.0)
    force_fail: bool | None = None


@app.get("/healthz", response_model=HealthResponse)
def healthz() -> HealthResponse:
    return HealthResponse(status="ok", service=SERVICE, version=settings.service_version)


@app.get("/readyz", response_model=HealthResponse)
def readyz() -> HealthResponse:
    return HealthResponse(status="ok", service=SERVICE, version=settings.service_version)


@app.get("/metrics")
def metrics() -> PlainTextResponse:
    return PlainTextResponse(metrics_payload().decode("utf-8"), media_type="text/plain; version=0.0.4")


@app.get("/v1/faults")
def get_faults() -> dict[str, Any]:
    return _state


@app.post("/v1/faults")
def set_faults(cfg: FaultConfig) -> dict[str, Any]:
    if cfg.latency_ms is not None:
        _state["latency_ms"] = cfg.latency_ms
    if cfg.fail_rate is not None:
        _state["fail_rate"] = cfg.fail_rate
    if cfg.force_fail is not None:
        _state["force_fail"] = cfg.force_fail
    return _state


@app.post("/v1/payments", response_model=PaymentResponse)
def charge(
    body: PaymentRequest,
    x_correlation_id: str | None = Header(default=None),
) -> PaymentResponse:
    _ = x_correlation_id
    latency = int(_state["latency_ms"])
    if latency:
        time.sleep(latency / 1000.0)
    should_fail = bool(_state["force_fail"]) or random.random() < float(_state["fail_rate"])
    if should_fail:
        raise HTTPException(status_code=502, detail="payment provider unavailable")
    return PaymentResponse(
        payment_id=uuid.uuid4(),
        status="captured",
        latency_ms=latency,
    )
