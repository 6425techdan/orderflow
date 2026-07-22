# Runbook: Queue backlog / age high

**ID:** RB-002  
**Alert:** `OrderFlowQueueBacklog`  
**Drill:** `scripts/drills/queue_backlog.py`  
**Scope:** Local Redis Streams — simulated backlog only

## Symptoms

- `orderflow_queue_depth` and/or `orderflow_queue_age_seconds` above thresholds
- Accept path may still be healthy while processing lags
- Customer-visible delay to terminal order state (in the lab UI/API)

## Impact (lab)

- SLO: queue freshness (p95 age &lt; 30s weekday) burns
- Stadium surge intentionally creates backlog — label demos as simulated

## Immediate mitigation

1. Check workers: `docker compose -f deploy/compose/docker-compose.yml ps order-worker`
2. If stopped for a drill: `docker compose -f deploy/compose/docker-compose.yml start order-worker`
3. Clear payment faults if workers are blocked on dependency errors
4. Optionally scale worker replicas on kind (HPA demo) — not required for Compose
5. Never flush Redis with `FLUSHALL` unless you accept losing lab stream state

## Diagnosis

| Check | Why |
|---|---|
| Worker crashloop / restarts | Consumer stopped |
| Payment errors / latency | Secondary backlog |
| k6 profile still running | Intentional load |
| DLQ depth | Poison messages vs throughput |

## Escalation

Capture queue depth/age panels; note whether backlog was drill-induced; reset load generators.

## Follow-up

Link from Alertmanager; include measured recovery time in postmortem.
