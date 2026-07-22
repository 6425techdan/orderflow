variable "name" {
  description = "ACR name (globally unique, alphanumeric only)."
  type        = string

  validation {
    condition     = can(regex("^[a-zA-Z0-9]{5,50}$", var.name))
    error_message = "name must be 5–50 alphanumeric characters (ACR global uniqueness rules)."
  }
}

variable "location" {
  description = "Azure region for the registry."
  type        = string

  validation {
    condition     = length(trimspace(var.location)) > 0
    error_message = "location must be a non-empty Azure region name."
  }
}

variable "resource_group_name" {
  description = "Resource group for the registry."
  type        = string

  validation {
    condition     = length(trimspace(var.resource_group_name)) > 0
    error_message = "resource_group_name must be non-empty."
  }
}

variable "sku" {
  description = "ACR SKU."
  type        = string
  default     = "Basic"

  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.sku)
    error_message = "sku must be Basic, Standard, or Premium."
  }
}

variable "admin_enabled" {
  description = "Enable admin user. Prefer false and use managed identity / AAD."
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags applied to the registry."
  type        = map(string)
  default     = {}
}
