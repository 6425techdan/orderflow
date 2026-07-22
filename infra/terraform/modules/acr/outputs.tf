output "id" {
  description = "Resource ID of the container registry."
  value       = azurerm_container_registry.this.id
}

output "name" {
  description = "Name of the container registry."
  value       = azurerm_container_registry.this.name
}

output "login_server" {
  description = "Login server hostname for the registry."
  value       = azurerm_container_registry.this.login_server
}

# Admin credentials are never outputted — use AAD / managed identity.
