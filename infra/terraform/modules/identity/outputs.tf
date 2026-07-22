output "id" {
  description = "Resource ID of the user-assigned identity."
  value       = azurerm_user_assigned_identity.this.id
}

output "principal_id" {
  description = "Principal (object) ID of the identity."
  value       = azurerm_user_assigned_identity.this.principal_id
}

output "client_id" {
  description = "Client ID of the identity."
  value       = azurerm_user_assigned_identity.this.client_id
}

output "tenant_id" {
  description = "Tenant ID of the identity."
  value       = azurerm_user_assigned_identity.this.tenant_id
}

output "federated_credential_id" {
  description = "ID of the GitHub OIDC federated credential when enabled; otherwise null."
  value       = try(azurerm_federated_identity_credential.github[0].id, null)
}

output "github_oidc_subject" {
  description = "Computed GitHub OIDC subject claim (empty when OIDC disabled)."
  value       = var.github_oidc_enabled ? local.github_subject : ""
}
