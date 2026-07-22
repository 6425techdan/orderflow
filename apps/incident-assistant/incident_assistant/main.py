from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from orderflow_common.models import HealthResponse
from orderflow_common.telemetry import AI_CALLS, AI_ESTIMATED_COST, AI_LATENCY, metrics_payload

from incident_assistant.engine import analyze, assert_no_infra_mutation_hooks
from incident_assistant.schemas import AssistantRequest, AssistantResponse

SERVICE = "incident-assistant"
assert_no_infra_mutation_hooks()

app = FastAPI(
    title="OrderFlow incident-assistant",
    version="0.1.0",
    description="Advisory-only fixture engine. No infrastructure mutations.",
)


@app.get("/healthz", response_model=HealthResponse)
def healthz() -> HealthResponse:
    return HealthResponse(status="ok", service=SERVICE, version="0.1.0")


@app.get("/metrics")
def metrics() -> PlainTextResponse:
    return PlainTextResponse(metrics_payload().decode("utf-8"), media_type="text/plain; version=0.0.4")


@app.post("/v1/analyze", response_model=AssistantResponse)
def analyze_incident(body: AssistantRequest) -> AssistantResponse:
    """Advisory analysis only. Never mutates infrastructure."""
    if body.mode != "fixture":
        # Live mode still routes through the same engine unless a provider is wired later.
        body.mode = "fixture"
    result = analyze(body)
    AI_CALLS.labels(SERVICE, result.mode, "ok").inc()
    AI_LATENCY.labels(SERVICE, result.mode).observe(result.latency_ms / 1000.0)
    AI_ESTIMATED_COST.labels(SERVICE).inc(result.estimated_cost_usd)
    return result


@app.post("/v1/actions/execute")
def refuse_execute(payload: dict[str, object]) -> dict[str, object]:
    return {
        "accepted": False,
        "reason": "incident-assistant cannot execute actions; human authorization required",
        "requested": payload,
        "mutates_infra": False,
    }


def _load_request(path: Optional[Path]) -> AssistantRequest:
    raw: Any = json.load(sys.stdin) if path is None else json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "request" in raw:
        raw = raw["request"]
    return AssistantRequest.model_validate(raw)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="OrderFlow incident assistant (fixture/CLI)")
    parser.add_argument("--fixture", type=Path, help="Fixture JSON path (stdin if omitted)")
    parser.add_argument(
        "--refuse",
        default="",
        help="Print refusal payload for a proposed action string",
    )
    parser.add_argument("--serve", action="store_true", help="Serve FastAPI on --host/--port")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8090)
    args = parser.parse_args(argv)

    if args.refuse:
        print(json.dumps(refuse_execute({"action": args.refuse}), indent=2))
        return 0

    if args.serve:
        import uvicorn

        uvicorn.run(app, host=args.host, port=args.port)
        return 0

    result = analyze(_load_request(args.fixture))
    print(result.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
