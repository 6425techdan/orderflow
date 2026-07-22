# Repair loop — 2026-07-22

**Objective:** Close interview-ready gaps: prove Compose e2e, wire Alertmanager + linked traces, real screenshots, honest docs, kind rehearsal, push CI green.

**Acceptance criteria (operator evidence):**

1. `make up` + `make e2e` succeed (accept → process → persist).
2. Prometheus scrapes healthy; Alertmanager shows firing lab alerts; Tempo shows API→worker linked traces via Redis `traceparent`.
3. Real `docs/screenshots/grafana-red-queue.png` from live Grafana.
4. Roadmap / architecture / walkthrough / ORR match proven runtime (no aspirational “complete” without evidence).
5. kind rollout/rollback rehearsed **or** honestly deferred.
6. Initial commit pushed; existing GitHub Actions `ci` green (no Compose/kind CI jobs this loop).

**Out of scope:** Azure apply, Loki app log shipping, Chaos Mesh, image attestations, expanding CI to Compose e2e.

**Honesty notes:**

- Loki container is present; apps do **not** ship logs to Loki yet.
- `deploy/chaos/` remains empty; drills live under `scripts/drills/`.
- Alertmanager uses a null receiver — UI visibility only, not paging.
