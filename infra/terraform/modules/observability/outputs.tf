output "workspace_id" {
  description = "Resource ID of the Log Analytics workspace."
  value       = azurerm_log_analytics_workspace.this.id
}

output "workspace_name" {
  description = "Name of the Log Analytics workspace."
  value       = azurerm_log_analytics_workspace.this.name
}

output "workspace_customer_id" {
  description = "Workspace (customer) ID used by agents."
  value       = azurerm_log_analytics_workspace.this.workspace_id
}

# Intentionally omit primary_shared_key — never embed Log Analytics keys in Terraform outputs.
