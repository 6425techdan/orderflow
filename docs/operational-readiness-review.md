# Operational Readiness Review (ORR)

**System:** 6425 Reliability Lab: OrderFlow  
**Honesty:** Personal lab ORR — not an enterprise launch gate.

## Checklist

### Dependencies and failure modes

- [x] Critical path documented — [architecture.md](architecture.md)
- [x] Runbooks for payment, queue, latency — `docs/runbooks/`
- [x] Drill scripts — `scripts/drills/`
- [x] Idempotency / retries — ADR-005 + unit tests

### Observability

- [x] RED + queue dashboards — `observability/dashboards/`
- [x] OTel pipeline in Compose
- [x] Symptom alerts → runbooks — `observability/alerts/rules.yml` + Alertmanager in Compose
- [x] Screenshots on *your* machine under `docs/screenshots/` (operator) — `grafana-red-queue.png` (2026-07-22)

### Change and delivery

- [x] Quick start — [interview-walkthrough.md](interview-walkthrough.md)
- [x] kind rollout/rollback rehearsed if claiming live K8s (2026-07-22 lab rehearsal)
- [x] CI — `.github/workflows/ci.yml`, `supply-chain.yml`, `terraform.yml` (no apply)
- [x] Prod-like protection design — [oidc-azure.md](oidc-azure.md)

### Capacity and cost

- [x] Load profiles labeled simulated — `tests/load/`
- [x] [capacity-plan.md](capacity-plan.md), [cost-model.md](cost-model.md)
- [x] Azure STOP gate respected

### Security

- [x] `.env.example` only; secrets gitignored
- [x] [threat-model.md](threat-model.md)
- [x] AI non-mutate — [ai-safety-and-verification.md](ai-safety-and-verification.md)

### Ownership and response

- [x] [service-ownership.md](service-ownership.md)
- [x] Postmortem — [INC-2026-07-lab-payment-surge.md](incidents/INC-2026-07-lab-payment-surge.md)
- [x] Teardown — `scripts/teardown/local.sh` / `local.ps1`

## Sign-off

| Role | Name | Date | Notes |
|---|---|---|---|
| Lab owner | Dan Lewis | 2026-07-22 | Lab ORR; Compose + screenshot captured; kind rehearsal optional before claiming live K8s |

## Non-claims

Passing this ORR does not mean multi-region production readiness, PCI compliance, or verified real-venue capacity.
