# Runbook: GitOps drift

**ID:** RB-006 (config / sync mismatch)  
**Scope:** OrderFlow Argo CD Applications vs live kind/cluster state. **Lab-only.**  
**Authority:** Human operator chooses reconcile direction (git→cluster or cluster→git). Agents must not force-prune without approval.

## Symptoms

- Argo CD Application shows `OutOfSync`
- Live objects differ from `deploy/kustomize/overlays/*`
- Manual `kubectl edit` / `rollout undo` / scale changes not reflected in git
- Self-heal repeatedly fighting operator changes (staging)

## Impact (lab)

Unclear source of truth, failed drills, accidental overwrite of intentional fault-injection state.

## Immediate mitigation

1. **Pause auto-sync** if self-heal is fighting a live experiment:

```bash
argocd app set orderflow-staging --sync-policy none
```

2. Capture current live vs desired:

```bash
argocd app diff orderflow-staging
argocd app diff orderflow-prod-like
kubectl -n orderflow get deploy,svc,hpa,pdb -o wide
```

## Diagnosis

| Check | Command / artifact |
|---|---|
| Desired manifests | `kubectl kustomize deploy/kustomize/overlays/staging` |
| Live objects | `kubectl -n orderflow get all` |
| Argo sync status | `argocd app get <app>` |
| Who changed live | `kubectl -n orderflow get events --sort-by=.lastTimestamp` |

Common lab drift sources:

- `demo-rollout-rollback` scripts changing image tags
- HPA adjusting `replicas` (ignored via `ignoreDifferences` on Deployments)
- Manual probe or env edits during drills
- Wrong overlay applied with plain `kubectl apply -k`

## Reconcile choices

### Prefer git as source of truth (default for staging)

```bash
argocd app sync orderflow-staging --prune
argocd app wait orderflow-staging --health
```

Re-enable auto-sync when done:

```bash
argocd app set orderflow-staging --sync-policy automated --auto-prune --self-heal
```

### Prefer live as temporary source (rare)

1. Export live manifests or note the intentional change.
2. Encode the change in the correct Kustomize overlay.
3. Commit, then sync so Argo matches git again.

Never leave long-lived live-only changes on prod-like without a git commit — the next sync will erase them.

## Verification

- Application `Synced` + `Healthy` (or documented degraded for a drill)
- `argocd app diff` empty (aside from ignored fields such as HPA-managed replicas)
- Overlay path matches intended environment label (`orderflow.lab/environment`)

## Escalation (solo lab)

If prune would delete lab data volumes or secrets you still need, abort sync, snapshot `kubectl get -o yaml`, then reconcile surgically.

## Follow-up

- Record whether drift was expected (drill) or accidental
- Tighten ignoreDifferences only when HPA/metrics-server is intentionally in play
- Prefer overlay patches over live edits for repeatable demos
