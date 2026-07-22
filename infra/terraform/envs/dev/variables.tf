provider "azurerm" {
  features {}
  # Auth via Azure CLI / Workload Identity / environment — never hard-code credentials.
  # subscription_id and tenant_id may be supplied via ARM_* env vars or tfvars (non-secret IDs only).
}

variable "subscription_id" {
  description = "Target Azure subscription ID (non-secret). Prefer ARM_SUBSCRIPTION_ID."
  type        = string
  default     = null
}

variable "tenant_id" {
  description = "Azure AD tenant ID for Key Vault."
  type        = string

  validation {
    condition     = can(regex("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$", var.tenant_id))
    error_message = "tenant_id must be a UUID."
  }
}

variable "location" {
  description = "Azure region."
  type        = string
  default     = "eastus"

  validation {
    condition     = length(trimspace(var.location)) > 0
    error_message = "location must be non-empty."
  }
}

variable "name_prefix" {
  description = "Short prefix for resource naming."
  type        = string
  default     = "of-dev"

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]{1,20}[a-z0-9]$", var.name_prefix))
    error_message = "name_prefix must be 3–22 lowercase alphanumeric with optional hyphens."
  }
}

variable "resource_group_name" {
  description = "Primary resource group name."
  type        = string
  default     = "rg-orderflow-dev"
}

variable "acr_name" {
  description = "Globally unique ACR name."
  type        = string
  default     = "acroforderflowdev"

  validation {
    condition     = can(regex("^[a-zA-Z0-9]{5,50}$", var.acr_name))
    error_message = "acr_name must be 5–50 alphanumeric characters."
  }
}

variable "key_vault_name" {
  description = "Key Vault name (globally unique-ish)."
  type        = string
  default     = "kv-orderflow-dev"

  validation {
    condition     = can(regex("^[a-zA-Z][a-zA-Z0-9-]{1,22}[a-zA-Z0-9]$", var.key_vault_name))
    error_message = "key_vault_name must be a valid Key Vault name."
  }
}

variable "state_storage_account_name" {
  description = "Storage account for Terraform state (bootstrap / module)."
  type        = string
  default     = "stofdevtfstate"

  validation {
    condition     = can(regex("^[a-z0-9]{3,24}$", var.state_storage_account_name))
    error_message = "state_storage_account_name must be 3–24 lowercase alphanumeric."
  }
}

variable "aks_system_node_count" {
  description = "System pool node count (lab-modest)."
  type        = number
  default     = 1

  validation {
    condition     = var.aks_system_node_count >= 1 && var.aks_system_node_count <= 3
    error_message = "aks_system_node_count for dev must be 1–3."
  }
}

variable "aks_system_vm_size" {
  description = "System pool VM size."
  type        = string
  default     = "Standard_B2s"
}

variable "workload_identity_enabled" {
  description = "Enable AKS workload identity."
  type        = bool
  default     = true
}

variable "github_oidc_enabled" {
  description = "Create GitHub OIDC federated credential placeholders."
  type        = bool
  default     = false
}

variable "github_organization" {
  description = "GitHub org/user for OIDC (placeholder until enabled)."
  type        = string
  default     = "REPLACE_GITHUB_ORG"
}

variable "github_repository" {
  description = "GitHub repository for OIDC (placeholder until enabled)."
  type        = string
  default     = "orderflow"
}

variable "tags" {
  description = "Common tags."
  type        = map(string)
  default = {
    project     = "orderflow"
    environment = "dev"
    managed_by  = "terraform"
    cost_center = "lab"
  }
}
