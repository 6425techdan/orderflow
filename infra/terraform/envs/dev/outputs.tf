output "resource_group_name" {
  value = module.network.resource_group_name
}

output "aks_cluster_name" {
  value = module.aks.cluster_name
}

output "acr_login_server" {
  value = module.acr.login_server
}

output "key_vault_uri" {
  value = module.keyvault.vault_uri
}

output "log_analytics_workspace_id" {
  value = module.observability.workspace_id
}

output "github_oidc_subject" {
  value = module.identity.github_oidc_subject
}

output "tfstate_storage_account_name" {
  value = module.storage_state.storage_account_name
}
