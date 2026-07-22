# INC-2026-07-lab-payment-surge — Blameless postmortem

- **Date:** 2026-07-22 (lab drill window)
- **Authors:** Dan Lewis (solo lab owner)
- **Severity (lab scale):** SEV-2 (demo-impacting; no real customers)
- **Status:** Final (lab)
- **Related drill:** `scripts/drills/payment_failure.py` during synthetic lunch-style load

## Summary

During a scheduled reliability drill, `payment-mock` was configured with a high failure rate while synthetic order traffic continued. Payment call errors rose, workers retried/circuit-broke, and queue age increased. The accept path remained partially available. Faults were cleared; processing recovered. **No real payments, restaurants, or Azure resources were involved.**

## Impact (measured / recorded for this lab write-up)

| Signal | Observation | Notes |
|---|---|---|
| Drill duration | ~60s fault injection (+ brief recovery) | Script default window |
| Payment failures | Elevated while `force_fail` / high `fail_rate` active | From payment-mock fault API |
| Queue | Age/depth increased while workers blocked on payment | Expected secondary symptom |
| Real customer impact | **None** | Simulated clients / k6 only |
| Data loss | None intended; lab Postgres retained | No FLUSHALL / volume delete |

Exact Prometheus export values should be attached as screenshots under `docs/screenshots/` when captured on the demo machine. Until attached, treat numeric SLO burn as **qualitative** for this write-up — do not invent percentages.

## Detection

- Manual/drill awareness (operator started the script)
- Alert intent: `OrderFlowPaymentErrors` + `OrderFlowQueueBacklog` (`observability/alerts/rules.yml`)
- Optional: incident-assistant fixture `tests/eval/fixtures/inc_payment_surge.json` ranked `payment_dependency` in top hypotheses

## Timeline (lab clock)

| Time (relative) | Event |
|---|---|
| T+0 | Baseline e2e order succeeds |
| T+1m | Optional k6 weekday/lunch started |
| T+2m | `payment_failure.py` injects faults |
| T+2–3m | Payment errors visible; queue pressure builds |
| T+3m | Runbook RB-001 followed; faults reset in script `finally` |
| T+4m | Workers process backlog; demo continues |
| T+5m | Notes captured for this postmortem |

## Root causes

### Facts

- Fault injection on `payment-mock` was enabled by the drill script
- Worker depends on payment for completion path
- Queue is at-least-once; backlog is a natural consequence of slow/failed processing

### Hypotheses (not required to explain this drill)

- Unrelated code regression — **rejected** (fault API confirmed injection)
- Cloud regional outage — **N/A** (local lab)

## What went well

- Fault API made dependency failure trivial to reproduce and reset
- Symptom-oriented alerts/runbooks map cleanly to the drill
- Assistant fixture mode stayed advisory and refused destructive actions

## What went poorly

- Without pre-started dashboards, screenshots can be missed mid-drill
- Lunch + payment fail together can obscure which signal is primary (teach correlation)

## Action items

| Item | Owner | Status |
|---|---|---|
| Keep RB-001 linked from alert annotations | Lab owner | Done in `rules.yml` |
| Capture Grafana screenshots on next rehearsal | Lab owner | Open |
| Ensure CI eval suite stays green for fixtures | Lab owner | `tests/eval/` |
| Do not claim real multi-restaurant outage in README | Lab owner | Policy |

## Appendix — honesty statement

This incident is a **portfolio drill record**. It exists to practice blameless writing, SLO language, and runbook use — not to document a production outage.
