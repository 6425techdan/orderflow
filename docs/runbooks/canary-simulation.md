# Runbook: Canary simulation (manual rollback authority)

**Scope:** Simulated canary for OrderFlow on kind/GitOps. **Not** a real progressive delivery controller (no Flagger/Argo Rollouts required).  
**Label honestly:** this is a **lab canary simulation** — traffic split is approximate (replica weighting), not production market volume.

## Goal

Practice a small blast-radius rollout of `order-api` (and optionally `order-worker`), observe health, then either continue or **manually roll back**. A human retains rollback authority at every step.

## Preconditions

- kind cluster up (`scripts/demo/kind-up.sh` or `.ps1`)
- Images available (`orderflow/order-api:<tag>` loaded into kind for local overlay)
- Baseline healthy:

```bash
kubectl -n orderflow get pods
kubectl -n orderflow rollout status deploy/order-api
```

## Simulation design (facts vs assumptions)

| Item | Status |
|---|---|
| Two ReplicaSets via rolling update | **Fact** — native Deployment strategy |
| True weighted traffic split / header routing | **Not implemented** — assumption that fewer new pods ≈ smaller exposure |
| Automated analysis / auto-promote | **Out of scope** — human decides |
| Manual rollback authority | **Required** — operator owns undo/sync revert |

## Procedure

### 1. Record baseline revision

```bash
kubectl -n orderflow rollout history deploy/order-api
BASELINE=$(kubectl -n orderflow get deploy/order-api -o jsonpath='{.status.observedGeneration}')
echo "baseline generation=$BASELINE"
```

### 2. Start “canary” by rolling a new image with surge=1

Local overlay already uses `maxSurge: 1` / `maxUnavailable: 0`. Set a new tag deliberately:

```bash
kubectl -n orderflow set image deploy/order-api order-api=orderflow/order-api:canary-sim
kubectl -n orderflow rollout status deploy/order-api --timeout=180s
```

Watch old and new pods coexist briefly:

```bash
kubectl -n orderflow get rs,pods -l app.kubernetes.io/name=order-api -o wide
```

### 3. Observe (human gate)

Check for 2–5 minutes (lab clock, not production soak):

```bash
kubectl -n orderflow get pods -l app.kubernetes.io/name=order-api
kubectl -n orderflow logs -l app.kubernetes.io/name=order-api --tail=50
# Optional: port-forward and hit /healthz /readyz /orders
kubectl -n orderflow port-forward svc/order-api 8080:8080
```

**Promote criteria (lab):** Ready pods stable, no CrashLoop, accept path works.  
**Abort criteria:** CrashLoop, readiness flaps, error spike, operator discomfort.

### 4A. Abort — manual rollback (preferred fast path)

```bash
kubectl -n orderflow rollout undo deploy/order-api
kubectl -n orderflow rollout status deploy/order-api
```

If Argo CD staging self-heal is on, pause sync first (see `gitops-drift.md`) or revert the git tag and sync.

### 4B. Continue — treat canary as full rollout

Leave the new ReplicaSet at full replica count. Encode the image tag in the overlay and commit so GitOps matches live state.

### 5. Prod-like Argo path (optional)

`orderflow-prod-like` has **no automated sync**. Operator sequence:

1. Merge/bump tag in `deploy/kustomize/overlays/prod-like`
2. `argocd app sync orderflow-prod-like` only after human approval
3. On failure: `argocd app rollback orderflow-prod-like <history-id>` **or** git revert + sync

## Rollback authority

| Role | May propose | May execute cluster rollback |
|---|---|---|
| Human lab owner | Yes | **Yes (sole authority)** |
| AI agent | Yes | **No** — wait for explicit approval |
| Automated sync (staging) | N/A | May overwrite live undo; pause before drills |

## Verification after abort or promote

- Desired ReplicaSet owns all Ready pods
- `docs/runbooks/rollback.md` verification checks pass
- Note drill outcome: promoted / aborted, time-to-decide, signals used

## Out of scope

- Real PSP / paid cloud canaries
- Claiming percentage-accurate traffic split without a service mesh or ingress weights
- Auto-rollback controllers
