# Azure Deployment Plan (OrderFlow)

**Status:** Plan-only by default  
**Related:** [cost-model.md](cost-model.md), [ADR-003](adr/ADR-003-local-first-azure.md), [terraform-destroy.md](terraform-destroy.md), [terraform-state-recovery.md](terraform-state-recovery.md)

## Goal

Optionally stand up a small Azure lab (AKS + supporting modules) for interview depth. Default path remains Compose/kind at ~$0.

## Prerequisites

- Terraform `>= 1.7`, Azure CLI authenticated to the **intended personal/lab** subscription
- Provider: `hashicorp/azurerm` `~> 4.0` (see module `versions.tf`)
- Copied `envs/<env>/terraform.tfvars.example` → `terraform.tfvars` with real tenant ID and unique ACR/storage names
- No secrets in git (no SP passwords, keys, or kubeconfigs)

## Steps (validate → plan → STOP)

1. **Confirm cost model** — Refresh [cost-model.md](cost-model.md) for region/SKUs (~$150–400/mo lab ballpark when left running).
2. **Init (local state ok for dry runs)**
   ```bash
   cd infra/terraform/envs/dev
   terraform init
   ```
3. **Validate / format / lint (no cloud spend)**
   ```bash
   terraform fmt -recursive ../../
   terraform validate
   # from infra/terraform
   tflint --chdir=envs/dev
   terraform test
   ```
4. **Plan only**
   ```bash
   terraform plan -out=tfplan
   ```
   Review the plan for unexpected resources, public exposure, and SKUs.
5. **STOP — approval required**
   - [ ] Cost estimate updated and understood  
   - [ ] Explicit human approval recorded (chat / PR / issue)  
   - [ ] Correct subscription confirmed (not employer/prod)  
   - [ ] Teardown owner and window agreed ([terraform-destroy.md](terraform-destroy.md))  

6. **Apply only after approval** — `terraform apply tfplan` (or equivalent). Prefer Azure AD / OIDC; never embed credentials in `.tf` files.
7. **Remote state (optional later)** — Bootstrap `storage-state`, then uncomment `backend "azurerm"` in `versions.tf` with `use_azuread_auth = true`. See [terraform-state-recovery.md](terraform-state-recovery.md).

## Cost estimate pointer

Use [cost-model.md](cost-model.md). Illustrative idle-aware lab total is roughly **$150–400/mo** if AKS nodes stay up; local Compose/kind remains **~$0**.

## Teardown

After demos, follow [terraform-destroy.md](terraform-destroy.md). Destroy is also STOP-gated (wrong subscription risk).

## Out of scope

- Claiming production AKS capacity or real market volume
- Paid Azure without approval
- Autonomous agent apply/destroy
