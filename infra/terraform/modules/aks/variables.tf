variable "name" {
  description = "AKS cluster name."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$", var.name))
    error_message = "name must be a valid DNS label (1–63 lowercase alphanumeric / hyphen)."
  }
}

variable "location" {
  description = "Azure region for the AKS cluster."
  type        = string

  validation {
    condition     = length(trimspace(var.location)) > 0
    error_message = "location must be a non-empty Azure region name."
  }
}

variable "resource_group_name" {
  description = "Resource group that hosts the AKS cluster."
  type        = string

  validation {
    condition     = length(trimspace(var.resource_group_name)) > 0
    error_message = "resource_group_name must be non-empty."
  }
}

variable "dns_prefix" {
  description = "DNS prefix for the managed cluster."
  type        = string

  validation {
    condition     = can(regex("^[a-z]([a-z0-9-]{0,52}[a-z0-9])?$", var.dns_prefix))
    error_message = "dns_prefix must start with a letter and be a valid DNS label (max 54)."
  }
}

variable "kubernetes_version" {
  description = "Kubernetes version for the control plane (leave null for Azure default)."
  type        = string
  default     = null

  validation {
    condition     = var.kubernetes_version == null || can(regex("^[0-9]+\\.[0-9]+(\\.[0-9]+)?$", var.kubernetes_version))
    error_message = "kubernetes_version must be null or look like MAJOR.MINOR or MAJOR.MINOR.PATCH."
  }
}

variable "subnet_id" {
  description = "Subnet ID used by the system node pool."
  type        = string

  validation {
    condition     = can(regex("^/subscriptions/.+/resourceGroups/.+/providers/Microsoft.Network/virtualNetworks/.+/subnets/.+$", var.subnet_id))
    error_message = "subnet_id must be a full Azure subnet resource ID."
  }
}

variable "system_node_count" {
  description = "Node count for the system pool."
  type        = number
  default     = 1

  validation {
    condition     = var.system_node_count >= 1 && var.system_node_count <= 5
    error_message = "system_node_count must be between 1 and 5 for this lab module."
  }
}

variable "system_vm_size" {
  description = "VM size for the system node pool."
  type        = string
  default     = "Standard_B2s"

  validation {
    condition     = can(regex("^Standard_", var.system_vm_size))
    error_message = "system_vm_size must be an Azure Standard_* SKU."
  }
}

variable "workload_identity_enabled" {
  description = "Enable Azure AD Workload Identity on the cluster (requires OIDC issuer)."
  type        = bool
  default     = true
}

variable "oidc_issuer_enabled" {
  description = "Enable OIDC issuer for the cluster (required for workload identity)."
  type        = bool
  default     = true

  validation {
    condition     = !(var.workload_identity_enabled && !var.oidc_issuer_enabled)
    error_message = "oidc_issuer_enabled must be true when workload_identity_enabled is true."
  }
}

variable "log_analytics_workspace_id" {
  description = "Optional Log Analytics workspace ID for Container Insights. Null skips OMS agent."
  type        = string
  default     = null
}

variable "tags" {
  description = "Tags applied to the AKS cluster."
  type        = map(string)
  default     = {}
}
