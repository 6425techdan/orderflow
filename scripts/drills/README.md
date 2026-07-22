# Reliability drills (local Compose)

All scripts target `localhost` Compose services. Scale is simulated.

| Script | Scenario |
|---|---|
| `payment_failure.py` | Payment provider forced failure |
| `payment_latency.py` | Payment latency |
| `db_exhaustion.py` | API DB pool exhaustion fault |
| `queue_backlog.py` | Backlog under slow payments |
| `stale_menu.py` | Stale menu config (HTTP 409) |

Additional cluster drills (kind):

- Worker crash loop: `kubectl delete pod -l app=order-worker -n orderflow`
- Partial disruption: delete one API pod while HPA/PDB remain
- Bad deployment: see `scripts/demo/demo-rollout-rollback.*`
- AI latency/cost: exercise incident-assistant fixture mode and inspect `orderflow_ai_*` metrics

Reset faults after each drill.
