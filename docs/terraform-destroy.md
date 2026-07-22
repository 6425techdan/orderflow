# Terraform Destroy (Safe Procedure)

**STOP-gated.** Destroying Azure resources incurs risk (wrong subscription, orphaned disks, Key Vault purge). Requires the same explicit human approval as apply. See [azure-deployment-plan.md](azure-deployment-plan.md) and [cost-model.md](cost-model.md).

## Before destroy

1. Confirm **subscription** and **resource group** names match the intended lab (`rg-orderflow-dev` / `rg-orderflow-prod-like`).
2. Confirm no shared resources outside this stack are referenced.
3. Snapshot or export anything you still need (ACR images, Key Vault secrets you intentionally stored).
4. Note Key Vault soft-delete / purge protection — `prod-like` enables purge protection and may block immediate purge.
5. Record approval and intended teardown window.

## Procedure

```bash
cd infra/terraform/envs/dev   # or prod-like
terraform init
terraform plan -destroy -out=destroy.tfplan
# Review destroy plan carefully — every resource should be lab-owned.
# STOP: obtain explicit approval if not already granted for this destroy.
terraform apply destroy.tfplan
```

## After destroy

1. In Azure Portal / CLI, verify the resource group is empty or gone.
2. Remove any leftover public IPs, NICs, or disks if AKS left orphans (rare with managed identity + Azure CNI cleanup).
3. If remote state should also be retired, destroy the bootstrap `storage-state` account **last**, after all env states are empty — or retain it cheaply for history.
4. Update [cost-model.md](cost-model.md) revision notes that cloud spend should return to ~$0.

## Do not

- Run destroy against employer or unknown subscriptions
- Use `-auto-approve` in shared/CI contexts without explicit approval gates
- Force-purge Key Vaults unless you understand recovery implications
- Commit destroy plan files containing sensitive computed values

## Local-first reminder

If the goal is “stop paying,” also stop any always-on SKUs and prefer Compose/kind for ongoing demos.
