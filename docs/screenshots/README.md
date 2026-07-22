# Dashboard screenshots

Capture Grafana **OrderFlow RED + Queue + SLO** after `make up` + load/drill and save as `grafana-red-queue.png` in this directory.

## How to capture

1. `make up` then `make e2e` (optionally `make drill-payment-fail`).
2. Open http://localhost:3000/d/orderflow-red-queue/orderflow-red-queue-slo?orgId=1&refresh=5s
3. Confirm panels show live series (HTTP rate, queue, payment ratio).
4. Either:
   - Manual: browser screenshot → `docs/screenshots/grafana-red-queue.png`
   - Automated (lab helper): `python scripts/demo/capture_grafana.py` (requires Playwright)

Do not commit fabricated images — only real screenshots from your environment.

**Alertmanager UI (local):** http://localhost:9093/#/alerts  
**Prometheus targets:** http://localhost:9090/targets  
**Tempo:** explore via Grafana datasource `Tempo` (API→worker linked via `traceparent` on Redis Streams).
