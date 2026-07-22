# Runbooks

Symptom-oriented operator guides for the OrderFlow **lab**. Each runbook links to drills and alerts where applicable.

## How to use

1. Confirm you are on the local Compose/kind stack (not a real production estate).
2. Follow immediate mitigation before deep diagnosis.
3. Capture metrics/screenshots; reset fault injection.
4. File or update a blameless note under `docs/incidents/` when impact was measured.

## Index

| ID | Title | Trigger | Doc |
|---|---|---|---|
| RB-001 | Payment dependency latency / errors | `OrderFlowPaymentErrors` / payment drill | [payment-dependency.md](payment-dependency.md) |
| RB-002 | Queue backlog / age high | `OrderFlowQueueBacklog` | [queue-backlog.md](queue-backlog.md) |
| RB-003 | High order latency | `OrderFlowHighOrderLatency` / payment latency | [high-order-latency.md](high-order-latency.md) |
| RB-004 | Postgres saturation | `OrderFlowDbPoolExhaustion` | See `scripts/drills/db_exhaustion.py` |
| RB-005 | Bad deploy rollback | Error spike after rollout | kind/Compose rollback (operator) |
| RB-006 | Stale / wrong config | Menu reject skew | `scripts/drills/stale_menu.py` |
| RB-007 | Partial disruption | Subset unhealthy | PDB/replica demos |
| RB-008 | AI assistant | Eval / advisory only | [ai-safety-and-verification.md](../ai-safety-and-verification.md) |

## Conventions

- Prefer symptom-based titles over “Redis is down.”
- Include verification commands that work in Compose; note kind differences.
- Never paste real secrets; use placeholders.
- Label simulated load and drills honestly.
