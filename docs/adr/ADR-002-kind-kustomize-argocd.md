# ADR-002: kind + Kustomize + Argo CD

- **Status:** Accepted
- **Date:** 2026-07-22
- **Deciders:** OrderFlow portfolio owner (Dan Lewis); platform lead for this lab

## Context

The lab must show Kubernetes reliability controls and GitOps without requiring paid cloud by default. Alternatives:

| Layer | Options considered |
|---|---|
| Local cluster | kind vs k3d vs minikube |
| Manifests | Kustomize vs Helm charts |
| GitOps | Argo CD vs Flux |

## Decision

1. **kind** for the local Kubernetes cluster (and CI-friendly cluster creation scripts).
2. **Kustomize** with `base` + overlays (`local`, `staging`, `prod-like`) for app/env separation.
3. **Argo CD** on kind for sync, health, drift demonstration, and rollback runbooks.

Progressive delivery: **documented canary simulation** plus Argo sync/rollback. Full Flagger / service-mesh canary is **out of scope** unless later justified.

## Consequences

**Positive**

- Common interviewer-familiar toolchain; kind is widely used in CI examples.
- Kustomize avoids Helm chart sprawl for a small service set.
- Argo CD gives a concrete GitOps story without Azure dependency.

**Negative / trade-offs**

- kind is not production AKS; cloud differences must be called out honestly in docs.
- Without Flagger, canary is simulated — do not claim automated traffic shifting.
- Flux was not chosen; switching later would be a new ADR.

**Follow-ups**

- Phase 3: kind bootstrap + reliability controls in overlays.
- Phase 5: Argo Application manifests and rollback runbook.
