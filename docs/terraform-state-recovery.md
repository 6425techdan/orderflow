# Terraform State Recovery

**Scope:** OrderFlow `infra/terraform` remote state on Azure Blob (`modules/storage-state`).  
**STOP:** Do not create paid storage or mutate production-like subscriptions without approval.

## Facts

- Desired backend: `backend "azurerm"` with `use_azuread_auth = true` (commented in `envs/*/versions.tf` until approved).
- Modules intentionally **do not output** storage account keys or connection strings.
- Blob versioning is enabled on the state storage account for accidental overwrite recovery.

## Import existing resources into state

Use when Azure resources already exist but Terraform state is empty/partial:

```bash
cd infra/terraform/envs/dev
terraform init
# Example shapes — replace IDs with real resource IDs from Azure.
terraform import 'module.network.azurerm_resource_group.this' /subscriptions/<sub>/resourceGroups/<rg>
terraform import 'module.network.azurerm_virtual_network.this' /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Network/virtualNetworks/<vnet>
terraform import 'module.aks.azurerm_kubernetes_cluster.this' /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.ContainerService/managedClusters/<aks>
```

Then `terraform plan` and reconcile drift (prefer updating code to match reality for lab resources).

## Recover from corrupted or missing local state

1. Confirm remote backend container and key (`orderflow/dev.tfstate` or `orderflow/prod-like.tfstate`).
2. Authenticate with Azure AD (`az login` or OIDC); avoid pasting account keys into shell history/files.
3. Re-init with backend config:
   ```bash
   terraform init -reconfigure
   ```
4. If a bad state blob was written, restore a prior **blob version** from the storage account (versioning enabled), then `terraform init` + `terraform plan`.
5. As last resort: `terraform state pull` to a secure local backup, fix JSON offline, `terraform state push` only with peer review — never commit state files.

## Lost state with live resources

1. Inventory resources by tag (`project=orderflow`, `environment=...`).
2. Import in dependency order (RG → network → identity/ACR/KV/LAW → AKS).
3. Run plan until empty (or documented intentional drift).
4. Document recovery in an incident note if this was an accidental destroy/outage drill.

## Assumptions / recommendations

- Prefer one state file per environment key; never share `dev` and `prod-like` keys.
- Locking is provided by the azurerm backend blob lease — do not disable it.
- If state may contain sensitive computed attrs, treat backups as secrets.
