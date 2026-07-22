output "storage_account_id" {
  description = "Resource ID of the Terraform state storage account."
  value       = azurerm_storage_account.tfstate.id
}

output "storage_account_name" {
  description = "Name of the Terraform state storage account."
  value       = azurerm_storage_account.tfstate.name
}

output "container_name" {
  description = "Blob container used for remote state."
  value       = azurerm_storage_container.tfstate.name
}

output "primary_blob_endpoint" {
  description = "Primary blob endpoint URL."
  value       = azurerm_storage_account.tfstate.primary_blob_endpoint
}

# Intentionally omit access keys / connection strings — configure backend via Azure CLI / OIDC.
