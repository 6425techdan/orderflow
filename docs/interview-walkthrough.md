# Interview Walkthrough

**Rule:** Only claim what you can run. Label synthetic load honestly.

## Narrative (30–40 minutes)

1. **Problem framing** — Fictional ordering platform; simulated multi-location load; SRE/platform portfolio.
2. **Architecture** — [architecture.md](architecture.md); Redis Streams (ADR-001); local-first (ADR-003).
3. **Happy path** — `make up` → `make e2e` (or `python scripts/demo/e2e_order.py`).
4. **Observability** — Grafana RED + queue ([screenshot](screenshots/grafana-red-queue.png)); Alertmanager at `:9093`; one API→worker Tempo trace (`traceparent` on the stream message).
5. **Kubernetes (optional)** — kind overlay; rollout/rollback if prepared (`scripts/demo/kind-up.ps1` / `.sh`, then `demo-rollout-rollback.*`).
6. **Failure drill** — `python scripts/drills/payment_failure.py` → [payment-dependency.md](runbooks/payment-dependency.md).
7. **Delivery** — `.github/workflows/ci.yml` + `supply-chain.yml`; OIDC design ([oidc-azure.md](oidc-azure.md)) without apply.
8. **Optional Azure** — Terraform modules + fmt/validate workflow; STOP + [cost-model.md](cost-model.md).
9. **AI assistant** — fixture CLI + evals ([ai-safety-and-verification.md](ai-safety-and-verification.md)).
10. **Close** — [INC-2026-07-lab-payment-surge.md](incidents/INC-2026-07-lab-payment-surge.md); deliberate non-goals.

## Commands

```bash
python -m pip install -e ".[dev]"
make up
make e2e
# optional load (label as synthetic):
k6 run tests/load/weekday.js
python scripts/drills/payment_failure.py
# From repo root with PYTHONPATH including apps/incident-assistant (pytest pythonpath already does):
python -m incident_assistant --fixture tests/eval/fixtures/payment_failure.json
# Windows: pwsh scripts/teardown/local.ps1
# Unix:    bash scripts/teardown/local.sh
```

## Honesty prompts

- “This traffic is synthetic.”
- “Exactly-once enough means idempotent handlers on at-least-once delivery.”
- “I will not apply Terraform without a cost estimate and approval.”
- “The assistant advises; it never mutates infra.”
- “Loki is in Compose for future log shipping; today dashboards and traces are the primary demo.”
