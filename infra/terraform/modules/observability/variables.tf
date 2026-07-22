variable "name" {
  description = "Log Analytics workspace name."
  type        = string

  validation {
    condition     = can(regex("^[A-Za-z0-9][A-Za-z0-9-]{2,61}[A-Za-z0-9]$", var.name))
    error_message = "name must be 4–63 characters, start/end alphanumeric, hyphens allowed."
  }
}

variable "location" {
  description = "Azure region for the workspace."
  type        = string

  validation {
    condition     = length(trimspace(var.location)) > 0
    error_message = "location must be a non-empty Azure region name."
  }
}

variable "resource_group_name" {
  description = "Resource group for the workspace."
  type        = string

  validation {
    condition     = length(trimspace(var.resource_group_name)) > 0
    error_message = "resource_group_name must be non-empty."
  }
}

variable "sku" {
  description = "Log Analytics SKU."
  type        = string
  default     = "PerGB2018"

  validation {
    condition     = contains(["PerGB2018", "CapacityReservation", "LACluster"], var.sku)
    error_message = "sku must be PerGB2018, CapacityReservation, or LACluster."
  }
}

variable "retention_in_days" {
  description = "Data retention in days."
  type        = number
  default     = 30

  validation {
    condition     = var.retention_in_days >= 30 && var.retention_in_days <= 730
    error_message = "retention_in_days must be between 30 and 730."
  }
}

variable "tags" {
  description = "Tags applied to the workspace."
  type        = map(string)
  default     = {}
}
