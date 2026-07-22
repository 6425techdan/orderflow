# Runbook: Payment dependency

**ID:** RB-001  
**Alert:** `OrderFlowPaymentErrors` / `PaymentDependencyFailure`  
**Drill:** `scripts/drills/payment_failure.py`  
**Scope:** Local `payment-mock` only — **not** a real PSP

## Symptom

Elevated `orderflow_payment_calls_total{result="failure"}`, worker retries/circuit open, secondary queue age rise.

## Impact (lab)

Synthetic order completion drops for the drill window; error budget may burn under lunch/stadium profiles.

## Immediate checks

1. `curl -s http://localhost:8082/v1/faults` — look for `force_fail` / high `fail_rate`
2. Worker logs for payment failures / circuit open
3. DLQ stream length (`orders-dlq`)

## Mitigation

```bash
python scripts/drills/payment_failure.py --reset-only
# or
curl -s -X POST http://localhost:8082/v1/faults \
  -H 'content-type: application/json' \
  -d '{"force_fail":false,"fail_rate":0,"latency_ms":0}'
```

If a bad deploy coincided, follow [rollback.md](rollback.md). Pause k6 stadium surge during recovery.

## Do not

- `terraform apply` / cluster destroy
- Call a real payment provider (none exists here)

## Escalation

Solo lab: freeze load, screenshot Grafana, draft postmortem notes.
