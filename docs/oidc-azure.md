# GitHub OIDC → Azure (design)

**Status:** Design only — no Azure resources are created by this document or by lab CI  
**Related:** [ADR-003](adr/ADR-003-local-first-azure.md), [ADR-007](adr/ADR-007-image-provenance.md), [cost-model.md](cost-model.md), `.github/workflows/drift.yml`

## Goal

Authenticate GitHub Actions to Azure **without long-lived client secrets**. Use short-lived OIDC tokens federated to an Azure AD application / managed identity, with GitHub Environments protecting prod-like paths.

## Non-goals

- Creating subscriptions, AKS, ACR, or Key Vault from this doc
- Storing `AZURE_CLIENT_SECRET` (or equivalent) in GitHub Secrets
- Allowing `terraform apply` from CI without a separate, reviewed, protected workflow

## Trust model

```text
GitHub Actions job
  → requests OIDC token (aud=api://AzureADTokenExchange)
  → Azure AD federated credential validates:
       repo, ref/environment, workflow subject claims
  → short-lived Azure access token
  → least-privilege RBAC on target scope
```

### Recommended identities (two)

| Identity | Purpose | Azure RBAC (illustrative) | GitHub Environment |
|---|---|---|---|
| `gha-orderflow-plan` | `terraform plan`, drift, ACR pull metadata | Reader + state storage blob reader | `azure-plan-readonly` (optional reviewers) |
| `gha-orderflow-deploy` | Image push / GitOps sync assist (if ever enabled) | AcrPush + limited AKS write | `azure-prod-like` (**required reviewers**) |

Never give Contributor/Owner to the plan identity. Never put deploy identity on unprotected `pull_request` from forks.

## Federated credential subject examples

Pin federation to **environment** for prod-like, and to **ref** for plan on `main`:

```text
# Plan on main only (example)
repo:<ORG>/<REPO>:ref:refs/heads/main

# Prod-like deploy via environment (preferred)
repo:<ORG>/<REPO>:environment:azure-prod-like
```

Avoid `repo:<ORG>/<REPO>:*` wildcards.

## Environment protection (prod-like)

Configure GitHub Environment `azure-prod-like`:

1. Required reviewers (lab owner at minimum)
2. Deployment branches: `main` only
3. Secrets: none for Azure auth (OIDC only); optional non-secret vars like `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`
4. Wait timer optional for demos

`azure-plan-readonly` may skip wait timers but should still restrict branches.

## Example login step (not enabled in this repo)

```yaml
permissions:
  contents: read
  id-token: write

# uses: azure/login@<FULL_40_CHAR_SHA>  # pin before enabling
# with:
#   client-id: ${{ vars.AZURE_CLIENT_ID }}
#   tenant-id: ${{ vars.AZURE_TENANT_ID }}
#   subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}
```

Pin `azure/login` to a full commit SHA the same way CI pins `actions/checkout`.

## Mapping to OrderFlow workflows

| Workflow | OIDC today | Intended later |
|---|---|---|
| `ci.yml` | No | No cloud |
| `supply-chain.yml` | No | Optional ACR push under `azure-prod-like` after approval |
| `terraform.yml` | No | Still fmt/validate only; plan via protected env |
| `drift.yml` | Documents intent | Plan-only OIDC under `azure-plan-readonly` |

## STOP gates

1. Human cost estimate reviewed ([cost-model.md](cost-model.md))
2. Explicit approval to create Azure resources
3. Federated credentials created manually (or via one-time approved Terraform)
4. Tear-down owner and schedule documented before long-lived clusters

## Honesty

OIDC design here is an interview-ready pattern. Until federation and a subscription exist, CI remains local-image and Python quality only — that is intentional for a local-first lab.
