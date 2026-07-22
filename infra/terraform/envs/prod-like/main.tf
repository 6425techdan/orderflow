# OrderFlow lab — Azure "prod-like" composition (plan / validate / test only by default).
# Larger node defaults than envs/dev, still modest lab SKUs — not production scale.
# STOP: Do not terraform apply without explicit approval. See docs/azure-deployment-plan.md.

module "network" {
  source = "../../modules/network"

  name_prefix         = var.name_prefix
  location            = var.location
  resource_group_name = var.resource_group_name
  tags                = var.tags
}

module "storage_state" {
  source = "../../modules/storage-state"

  name                = var.state_storage_account_name
  location            = var.location
  resource_group_name = module.network.resource_group_name
  container_name      = "tfstate"
  tags                = var.tags
}

module "observability" {
  source = "../../modules/observability"

  name                = "${var.name_prefix}-law"
  location            = var.location
  resource_group_name = module.network.resource_group_name
  retention_in_days   = 30
  tags                = var.tags
}

module "identity" {
  source = "../../modules/identity"

  name                = "${var.name_prefix}-uami-gha"
  location            = var.location
  resource_group_name = module.network.resource_group_name
  github_oidc_enabled = var.github_oidc_enabled
  github_organization = var.github_organization
  github_repository   = var.github_repository
  github_entity_type  = "environment"
  github_entity_name  = "prod-like"
  tags                = var.tags
}

module "acr" {
  source = "../../modules/acr"

  name                = var.acr_name
  location            = var.location
  resource_group_name = module.network.resource_group_name
  sku                 = "Standard"
  admin_enabled       = false
  tags                = var.tags
}

module "keyvault" {
  source = "../../modules/keyvault"

  name                       = var.key_vault_name
  location                   = var.location
  resource_group_name        = module.network.resource_group_name
  tenant_id                  = var.tenant_id
  sku_name                   = "standard"
  purge_protection_enabled   = true
  soft_delete_retention_days = 30
  tags                       = var.tags
}

module "aks" {
  source = "../../modules/aks"

  name                       = "${var.name_prefix}-aks"
  location                   = var.location
  resource_group_name        = module.network.resource_group_name
  dns_prefix                 = "${var.name_prefix}-aks"
  subnet_id                  = module.network.aks_subnet_id
  system_node_count          = var.aks_system_node_count
  system_vm_size             = var.aks_system_vm_size
  workload_identity_enabled  = var.workload_identity_enabled
  oidc_issuer_enabled        = var.workload_identity_enabled
  log_analytics_workspace_id = module.observability.workspace_id
  tags                       = var.tags
}
