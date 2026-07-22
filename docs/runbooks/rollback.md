# Runbook: Rollback (bad deploy)

**ID:** RB-005  
**Scope:** OrderFlow reliability lab (Compose/kind/GitOps). **Simulated / lab-only** — not production market traffic.  
**Authority:** A human operator decides when to roll back. Agents may propose steps; they do not execute irreversible cluster changes without approval.

## Symptoms

- Elevated 5xx or latency on `order-api` after a rollout
- `order-worker` CrashLoopBackOff or stalled queue age
- Readiness failing on new ReplicaSet pods
- Argo CD Application `Synced` but workload unhealthy

## Impact (lab)

Demo SLO burn, blocked accept/process path, failed drill narratives. No real customer blast radius.

## Immediate mitigation

1. **Freeze further deploys** — stop image tag bumps and Argo syncs.
2. **Decide rollback authority** — sole lab owner (or designated operator) owns the call.
3. Prefer **Kubernetes rollout undo** for speed; use **GitOps revert** when drift must stay honest.

## Diagnosis

```bash
kubectl -n orderflow get deploy,rs,pods
kubectl -n orderflow rollout history deploy/order-api
kubectl -n orderflow describe deploy/order-api
kubectl -n orderflow logs -l app.kubernetes.io/name=order-api --tail=100
```

If using Argo CD:

```bash
argocd app get orderflow-staging
argocd app get orderflow-prod-like
argocd app history orderflow-prod-like
```

## Rollback options

### A. Fast path — Deployment revision undo (kind / direct apply)

```bash
kubectl -n orderflow rollout undo deploy/order-api
kubectl -n orderflow rollout undo deploy/order-worker
kubectl -n orderflow rollout status deploy/order-api
kubectl -n orderflow rollout status deploy/order-worker
```

**Note:** With Argo CD self-heal enabled (staging), undo may be overwritten on the next sync. Either pause sync or follow option B.

### B. Honest GitOps path — revert git, then sync

1. Revert the commit that changed image tags / overlays.
2. Push to the tracked branch.
3. Sync Application (manual for prod-like):

```bash
argocd app sync orderflow-prod-like
argocd app wait orderflow-prod-like --health
```

### C. Scripted demo

```bash
./scripts/demo/demo-rollout-rollback.sh
# Windows: .\scripts\demo\demo-rollout-rollback.ps1
```

## Verification

- Pods Ready; no CrashLoopBackOff
- `curl`/`scripts/demo/e2e_order.py` against `order-api` succeeds
- Queue age / error metrics return to pre-incident baseline (lab dashboards)
- Document time-to-mitigate in the drill log

## Escalation (solo lab)

Document freeze: stop changing cluster/git until postmortem notes are written. Do not “fix” by deleting volumes unless the drill explicitly calls for it.

## Follow-up

- Capture root cause (bad image, probe, config, dependency)
- Add/adjust probe or canary simulation steps if the failure would have been caught earlier
- Restore Argo auto-sync only after git and live state match
