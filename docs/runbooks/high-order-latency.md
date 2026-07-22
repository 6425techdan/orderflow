# Runbook: High order latency

**ID:** RB-003 (latency symptom)  
**Alerts:** `OrderFlowHighOrderLatency`, `OrderFlowPaymentLatency`  
**Drills:** `scripts/drills/payment_latency.py`, load profiles under `tests/load/`  
**Scope:** Simulated local latency — not multi-region RTT

## Symptoms

- API `/v1/orders` p95 elevated (`orderflow_http_request_duration_seconds`)
- Payment p95 elevated (`orderflow_payment_latency_seconds`)
- End-to-end accept → completed stretched; traces show time in worker→payment

## Impact (lab)

- Latency SLO (accept p95 &lt; 300ms weekday on Compose) may miss under lunch/stadium
- Users (synthetic clients) see slow accepts or slow completion

## Immediate mitigation

1. Check active k6 profile — stop stadium surge if not intentional
2. Reset payment latency fault:
   ```bash
   python scripts/drills/payment_latency.py --reset-only
   ```
3. Verify DB pool not exhausted (see db drill)
4. Confirm OTel/Prometheus scrape is not the bottleneck (usually isn’t)

## Diagnosis

| Layer | Signal |
|---|---|
| Edge / API | RED dashboard for `order-api` |
| Queue | Age rising with healthy API → async path |
| Payment | Fault `latency_ms` or histogram |
| DB | Pool available / wait |

Prefer **symptom → dependency** over jumping to “Kubernetes is bad.”

## Escalation

Freeze load; screenshot traces; record whether fault injection was on.

## Follow-up

Tune alert `for:` durations so weekday noise doesn’t page during intentional drills.
