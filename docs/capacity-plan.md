# Capacity Plan

**Honesty:** Lab host + synthetic load — not capacity for ~300 real restaurants.

## Demand (simulated)

| Profile | Script | Intent |
|---|---|---|
| Weekday | `tests/load/weekday.js` | Baseline; CI-friendly |
| Lunch rush | `tests/load/lunch_rush.js` | Elevated arrival |
| Stadium surge | `tests/load/stadium_surge.js` | Stress / intentional budget burn |

Location IDs may number in the hundreds for narrative color only.

## Supply (local default)

| Resource | Assumption |
|---|---|
| Laptop / CI runner | Single-node Docker; optional kind |
| API / worker replicas | Start at 2 on kind; Compose usually 1 each |
| Postgres / Redis | Single instances — not HA |

## Saturation signals

API p95/errors, queue depth/age, payment latency/errors, `orderflow_db_pool_available`, worker lag.

## Azure

Only after STOP approval and cost review. CI does not apply Terraform.

## Measurement protocol

Record machine class, Compose vs kind, profile duration, whether drills were active. Never extrapolate laptop rps to real venues.
