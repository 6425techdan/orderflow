variable "name_prefix" {
  description = "Prefix for network-related resource names (letters, numbers, hyphens)."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]{1,20}[a-z0-9]$", var.name_prefix))
    error_message = "name_prefix must be 3–22 lowercase alphanumeric characters with optional hyphens, starting and ending with alphanumeric."
  }
}

variable "location" {
  description = "Azure region for the resource group and network resources."
  type        = string

  validation {
    condition     = length(trimspace(var.location)) > 0
    error_message = "location must be a non-empty Azure region name."
  }
}

variable "resource_group_name" {
  description = "Name of the Azure resource group to create."
  type        = string

  validation {
    condition     = can(regex("^[a-zA-Z0-9._\\-()]{1,90}$", var.resource_group_name))
    error_message = "resource_group_name must be 1–90 characters and use only letters, numbers, underscore, period, hyphen, or parentheses."
  }
}

variable "vnet_address_space" {
  description = "Address space for the virtual network."
  type        = list(string)
  default     = ["10.10.0.0/16"]

  validation {
    condition     = length(var.vnet_address_space) >= 1 && alltrue([for cidr in var.vnet_address_space : can(cidrhost(cidr, 0))])
    error_message = "vnet_address_space must contain at least one valid CIDR block."
  }
}

variable "aks_subnet_prefix" {
  description = "CIDR for the AKS node subnet."
  type        = string
  default     = "10.10.0.0/22"

  validation {
    condition     = can(cidrhost(var.aks_subnet_prefix, 0))
    error_message = "aks_subnet_prefix must be a valid CIDR block."
  }
}

variable "endpoints_subnet_prefix" {
  description = "CIDR for the private endpoints subnet."
  type        = string
  default     = "10.10.4.0/24"

  validation {
    condition     = can(cidrhost(var.endpoints_subnet_prefix, 0))
    error_message = "endpoints_subnet_prefix must be a valid CIDR block."
  }
}

variable "tags" {
  description = "Tags applied to network resources."
  type        = map(string)
  default     = {}
}
