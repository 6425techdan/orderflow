from __future__ import annotations

import re
import time
from typing import Any

from incident_assistant.schemas import (
    AssistantRequest,
    AssistantResponse,
    Confidence,
    Hypothesis,
)

FORBIDDEN = re.compile(
    r"\b(kubectl\s+delete|terraform\s+apply|terraform\s+destroy|rm\s+-rf|drop\s+table|az\s+aks\s+delete)\b",
    re.IGNORECASE,
)

# Declared forbidden runtime calls — this module must never invoke them.
FORBIDDEN_RUNTIME_CALLS = ("kubectl", "terraform", "az aks", "helm uninstall")


def assert_no_infra_mutation_hooks() -> None:
    """Fail fast if mutate-capable tooling is imported into the assistant process."""
    import sys

    banned = {"kubernetes", "azure.mgmt", "libcloud"}
    loaded = banned.intersection(sys.modules)
    if loaded:
        raise RuntimeError(f"incident assistant must not load mutate-capable modules: {sorted(loaded)}")
    # Source-level guarantee: no shell-out helper imports in this module.
    import inspect

    src = inspect.getsource(sys.modules[__name__])
    # Match import forms only so this docstring/check text does not self-trigger.
    if re.search(r"(?m)^\s*import subprocess\b|^\s*from subprocess\b", src):
        raise RuntimeError("incident assistant engine must not import shell helpers")

# Deterministic mapping from symptom signatures to root causes for fixture mode.
RULES: list[dict[str, Any]] = [
    {
        "root_cause_id": "payment_provider_failure",
        "title": "Payment provider elevated 5xx / forced failure",
        "match_alerts": ["PaymentDependencyFailure", "payment"],
        "match_telemetry": {"payment_success_ratio_lt": 0.95},
        "diagnostics": [
            "Check payment-mock /v1/faults",
            "Compare payment latency histogram",
            "Review worker dead-letter stream length",
        ],
    },
    {
        "root_cause_id": "payment_provider_latency",
        "title": "Payment provider latency spike",
        "match_alerts": ["PaymentLatencyHigh"],
        "match_telemetry": {"payment_p95_ms_gt": 500},
        "diagnostics": [
            "Inspect payment-mock latency_ms fault",
            "Check worker queue age while payments slow",
        ],
    },
    {
        "root_cause_id": "db_connection_exhaustion",
        "title": "Database connection pool exhaustion",
        "match_alerts": ["DatabaseUnavailable", "db_exhaust"],
        "match_telemetry": {"api_5xx_ratio_gt": 0.1},
        "diagnostics": [
            "Check order-api /v1/faults db_exhaust flag",
            "Inspect db pool available gauge",
        ],
    },
    {
        "root_cause_id": "queue_backlog",
        "title": "Order queue backlog / worker lag",
        "match_alerts": ["QueueAgeHigh", "queue"],
        "match_telemetry": {"queue_age_seconds_gt": 30},
        "diagnostics": [
            "Inspect Redis stream depth",
            "Scale workers or pause ingress load",
        ],
    },
    {
        "root_cause_id": "bad_deployment",
        "title": "Bad deployment / regression after rollout",
        "match_alerts": ["ErrorBudgetBurn", "deployment"],
        "match_telemetry": {"recent_deploy": True},
        "diagnostics": [
            "Compare revision before/after",
            "Execute documented rollback runbook",
        ],
    },
    {
        "root_cause_id": "stale_menu_config",
        "title": "Stale menu configuration rejected by API",
        "match_alerts": ["StaleMenu", "menu"],
        "match_telemetry": {"http_409_ratio_gt": 0.05},
        "diagnostics": [
            "Verify X-Menu-Version header vs configured menu_version",
            "Clear stale_menu_reject fault",
        ],
    },
]


def _alert_text(req: AssistantRequest) -> str:
    parts: list[str] = []
    for alert in req.alerts:
        parts.append(str(alert.get("name", "")))
        parts.append(str(alert.get("summary", "")))
    return " ".join(parts).lower()


def analyze(req: AssistantRequest) -> AssistantResponse:
    assert_no_infra_mutation_hooks()
    started = time.perf_counter()
    refused: list[str] = []
    notes: list[str] = [
        "Advisory only: no infrastructure mutations are performed.",
        "Facts are taken from provided alerts/telemetry; inferences are labeled separately.",
        f"Forbidden runtime calls (never executed): {', '.join(FORBIDDEN_RUNTIME_CALLS)}",
    ]

    blob = _alert_text(req) + " " + " ".join(req.runbook_excerpts).lower()
    if FORBIDDEN.search(blob):
        refused.append("Ignored prompt content that requested destructive actions.")

    # Prompt-injection resistance: strip instruction-like lines from runbooks used as evidence
    safe_runbooks = []
    for excerpt in req.runbook_excerpts:
        for line in excerpt.splitlines():
            if not line.strip().lower().startswith("ignore previous"):
                safe_runbooks.append(line)

    scored: list[tuple[int, Hypothesis]] = []
    telemetry = req.telemetry_summary
    for rule in RULES:
        score = 0
        facts: list[str] = []
        inferences: list[str] = []
        evidence: list[str] = []

        for token in rule["match_alerts"]:
            if token.lower() in blob:
                score += 3
                facts.append(f"Alert/context mentions '{token}'")
                evidence.append(f"alert:{token}")

        for key, threshold in rule.get("match_telemetry", {}).items():
            if key.endswith("_lt") and key[:-3] in telemetry:
                metric = key[:-3]
                if float(telemetry[metric]) < float(threshold):
                    score += 4
                    facts.append(f"Telemetry {metric}={telemetry[metric]} < {threshold}")
                    evidence.append(f"telemetry:{metric}")
            elif key.endswith("_gt") and key[:-3] in telemetry:
                metric = key[:-3]
                if float(telemetry[metric]) > float(threshold):
                    score += 4
                    facts.append(f"Telemetry {metric}={telemetry[metric]} > {threshold}")
                    evidence.append(f"telemetry:{metric}")
            elif key == "recent_deploy" and telemetry.get("recent_deploy"):
                score += 3
                facts.append(f"Recent deployment: {req.deployment.get('version', 'unknown')}")
                evidence.append("deployment:recent")

        if score <= 0:
            continue

        inferences.append(f"Pattern matches lab playbook for {rule['root_cause_id']}")
        if safe_runbooks:
            evidence.append("runbook:excerpt")

        if score >= 7:
            confidence = Confidence.HIGH
        elif score >= 4:
            confidence = Confidence.MEDIUM
        else:
            confidence = Confidence.LOW
        scored.append(
            (
                score,
                Hypothesis(
                    rank=0,
                    title=rule["title"],
                    root_cause_id=rule["root_cause_id"],
                    confidence=confidence,
                    facts=facts,
                    inferences=inferences,
                    evidence=evidence,
                    suggested_diagnostics=list(rule["diagnostics"]),
                    dangerous=False,
                ),
            )
        )

    scored.sort(key=lambda item: item[0], reverse=True)
    hypotheses = []
    for rank, (_score, hyp) in enumerate(scored[:5], start=1):
        hyp.rank = rank
        hypotheses.append(hyp)

    if not hypotheses:
        hypotheses.append(
            Hypothesis(
                rank=1,
                title="Insufficient evidence for confident root cause",
                root_cause_id="unknown",
                confidence=Confidence.LOW,
                facts=["No strong alert/telemetry signature matched known fixtures"],
                inferences=["Need broader telemetry or reproduction"],
                evidence=[],
                suggested_diagnostics=[
                    "Collect RED metrics",
                    "Check recent deploys",
                    "Review queue and payment dependency",
                ],
            )
        )

    refused.append("kubectl/terraform/cloud mutate actions are never executed by this assistant")
    latency_ms = int((time.perf_counter() - started) * 1000)
    return AssistantResponse(
        incident_id=req.incident_id,
        mode=req.mode,
        hypotheses=hypotheses,
        refused_actions=refused,
        latency_ms=latency_ms,
        token_consumption=0 if req.mode == "fixture" else 0,
        estimated_cost_usd=0.0,
        notes=notes,
    )
