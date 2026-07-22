# Cost Model

**Project:** 6425 Reliability Lab: OrderFlow  
**Status:** Phase 4 modules present — still **plan-only** until apply approval  
**Currency:** USD, rough monthly ranges for optional Azure only

## Principle

**Local-first.** The default demonstration path (Docker Compose and kind) should cost approximately **$0** beyond the operator’s existing machine and electricity. Optional Azure is an **additive** interview artifact and must never appear by accident.

## Local (near $0)

| Item | Estimate | Notes |
|---|---|---|
| Docker Compose stack | ~$0 | Postgres, Redis, apps, OTel backends on laptop |
| kind cluster | ~$0 | Local Kubernetes; Argo CD on kind |
| GitHub Actions (public free tier) | ~$0 within free minutes | Watch usage if private or heavy matrix |
| Paid LLM API | **$0 default** | Fixture/eval mode; paid model is STOP-gated |
| Terraform validate / `terraform test` / TFLint | ~$0 | No apply → no Azure bill |

**Assumptions:** Single developer machine; no always-on cloud VMs; no managed databases in the default path.

## Optional Azure (rough monthly USD)

These are **order-of-magnitude** ranges for a small personal lab, not a quote. Actual cost depends on region, SKU, uptime, egress, and Azure retail pricing at apply time. **STOP before any apply** — update this table with live calculator output and get explicit approval.

| Component (typical lab shape) | Rough monthly range (USD) | Notes |
|---|---|---|
| AKS control plane + small node pool (e.g. 1–2 small nodes, not always on) | ~$70–250 | Dominant cost; stop/deallocate when idle |
| Azure Container Registry (Basic/Standard) | ~$5–20 | Or reuse local images only and skip ACR initially |
| Key Vault | ~$0–5 | Operations-based; usually small at lab scale |
| Storage account (tfstate + logs) | ~$1–15 | Depends on retention and churn |
| Networking / public IP / egress | ~$5–40 | Easy to underestimate; keep private where possible |
| Log Analytics / managed observability extras | ~$0–100+ | Prefer in-cluster OSS on AKS; Azure Monitor adds cost |
| **Illustrative AKS lab total (typical)** | **~$150–400/mo** | Ballpark if left running; idle-aware lower; 24/7 larger SKUs higher |
| **Illustrative idle-aware / short-lived** | **~$80–250** | Tear down after demos; see [terraform-destroy.md](terraform-destroy.md) |

**Not included:** Reserved instances, support plans, multi-region, large load-test egress, third-party SaaS.

**Terraform layout:** `infra/terraform/modules/*` and `envs/dev` / `envs/prod-like` (`prod-like` defaults to modestly larger node count/VM size → expect toward the upper end of the lab band).

## Cost control rules

1. Prefer Compose/kind for demos and CI-like local proofs.
2. Never `terraform apply` without: updated estimate in this file, approval recorded (chat/PR/issue), and a teardown plan.
3. Tag all Azure resources for ownership and easy deletion.
4. Schedule teardown after demos; destroy is also STOP-gated (confirm no wrong subscription).
5. Load tests against cloud endpoints require a separate cost check (egress + compute).

## STOP gate (required)

Before creating paid Azure resources or running `terraform apply` / `destroy` against a real subscription:

- [ ] Cost estimate refreshed for the chosen region/SKUs  
- [ ] Explicit human approval obtained  
- [ ] Teardown steps documented and understood ([terraform-destroy.md](terraform-destroy.md))  
- [ ] Confirmation that no employer or production subscription is targeted  
- [ ] Deployment steps reviewed ([azure-deployment-plan.md](azure-deployment-plan.md))  

Until then, treat `infra/terraform/` as **plan / validate / test only**.

## Revision history

| Date | Change |
|---|---|
| 2026-07-22 | Initial Phase 0 draft with local ~$0 and rough AKS ranges |
| 2026-07-22 | Phase 4: align with Terraform modules; call out **$150–400/mo** AKS lab band and local **$0** |
