# SLOs and error budgets

**Honesty:** Lab targets for **simulated** traffic on local Compose/kind. Not contractual SLAs for real restaurants or venues.

## Service definition

Accept order → enqueue → worker (+ payment-mock) → durable terminal state. Synthetic location IDs and k6 profiles generate load only.

## SLOs

| SLO | Target | SLI |
|---|---|---|
| Order acceptance availability | 99.5% successful (non-5xx) over lab window | `orderflow_http_requests_total` on order routes |
| Order API latency | p95 &lt; 500 ms weekday profile | `orderflow_http_request_duration_seconds` |
| Queue freshness | Queue age p95 &lt; 30 s weekday | `orderflow_queue_age_seconds` |
| Payment dependency success | ≥ 95% success under weekday (when not fault-injecting) | `orderflow_payment_calls_total` |
| End-to-end process | p95 accept → terminal &lt; 5 s weekday | Traces / status timestamps |

### Profile expectations

| Profile | vs SLO |
|---|---|
| `tests/load/weekday.js` | Should generally meet lab targets |
| `tests/load/lunch_rush.js` | May approach burn |
| `tests/load/stadium_surge.js` | **Expected** to miss latency/queue SLOs — demo budget burn honestly |

## Error budget policy (affects releases)

1. Availability 99.5% ⇒ **0.5%** failure budget over the measurement window.
2. **Healthy budget:** normal merges and Compose/kind rollouts.
3. **Fast burn / exhausted:** freeze risky prod-like promotions; prefer rollback; run mitigation runbooks; write incident notes.
4. **Release gate:** if availability burn alert is firing, staging→prod-like promotion requires explicit human override documented in the PR.
5. CI lint/tests still run during freeze — freeze means not promoting risky runtime changes to the demo stack.

## Alerts

See `observability/alerts/rules.yml` — symptom-oriented, linked to runbooks.

## Evidence rule

Before claiming an SLO in an interview: cite profile, machine class, duration actually run, and screenshots. Label stadium results as stress, not production capacity.
