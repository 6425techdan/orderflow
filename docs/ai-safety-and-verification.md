# AI safety and verification

**Status:** Phase 7 — fixture/eval evidence in-repo  
**Related:** [ADR-006](adr/ADR-006-ai-assistant-boundaries.md), `apps/incident-assistant/`

## Principles

1. Incident assistant is **advisory only** — humans authorize every change.
2. Default mode is **deterministic fixtures** — no paid model API required.
3. Every recommendation must separate **facts** vs **inferences** and cite evidence.
4. The assistant **never** executes `kubectl`, Terraform, Azure mutations, or shell destructive actions.
5. `POST /v1/actions/execute` always refuses (`accepted: false`).
6. Inputs are sanitized summaries (alerts, telemetry digests, runbook excerpts) — not secrets or employer data.
7. Enabling a paid live model is an explicit **STOP gate** (cost + data handling).

## Evaluation

```bash
python -m pytest tests/eval -q
```

| Check | Evidence |
|---|---|
| Top-3 root cause | `tests/eval/fixtures/*.json` expected ids |
| Dangerous recommendations | Forbidden substrings absent from response JSON |
| Facts vs inference | Hypotheses carry both lists + evidence |
| Execute refusal | `/v1/actions/execute` returns `accepted: false` |
| Prompt injection | Runbook “ignore previous… kubectl delete” does not authorize mutate |
| No subprocess mutate | `assert_no_infra_mutation_hooks()` in engine |

Fixtures (3 known lab incidents): payment failure, queue backlog, bad deployment.

## CLI

```bash
# From repo with PYTHONPATH including apps/incident-assistant (pytest pythonpath already does)
python -m incident_assistant --fixture tests/eval/fixtures/payment_failure.json
python -m incident_assistant --refuse "terraform apply"
```

## GenAI telemetry (optional later)

Metrics: `orderflow_ai_calls_total`, `orderflow_ai_latency_seconds`, `orderflow_ai_estimated_cost_usd_total`.  
Fixture mode reports zero token/cost.

## Proof of non-autonomy

- No code path imports cloud SDKs for mutate.
- `/v1/analyze` is read-only; execute endpoint always refuses.
- CI/evals assert refusal and injection resistance.
- Humans authorize all infra changes per AGENTS.md STOP gates.

## Interview stance

Explain when you would **reject** model output, why Phases 1–6 come first, and how evals prove safety without spend.
