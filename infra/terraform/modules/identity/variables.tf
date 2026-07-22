variable "name" {
  description = "User-assigned managed identity name."
  type        = string

  validation {
    condition     = can(regex("^[a-zA-Z0-9][a-zA-Z0-9_-]{1,126}[a-zA-Z0-9]$", var.name))
    error_message = "name must be 3–128 characters, alphanumeric with underscore/hyphen allowed mid-string."
  }
}

variable "location" {
  description = "Azure region for the identity."
  type        = string

  validation {
    condition     = length(trimspace(var.location)) > 0
    error_message = "location must be a non-empty Azure region name."
  }
}

variable "resource_group_name" {
  description = "Resource group for the identity."
  type        = string

  validation {
    condition     = length(trimspace(var.resource_group_name)) > 0
    error_message = "resource_group_name must be non-empty."
  }
}

variable "github_oidc_enabled" {
  description = "When true, create a federated identity credential for GitHub OIDC (placeholders required)."
  type        = bool
  default     = false
}

variable "github_organization" {
  description = "GitHub org/user that issues OIDC tokens. Required when github_oidc_enabled."
  type        = string
  default     = ""

  validation {
    condition     = !var.github_oidc_enabled || can(regex("^[A-Za-z0-9_.-]+$", var.github_organization))
    error_message = "github_organization must be set to a valid GitHub org/user when github_oidc_enabled is true."
  }
}

variable "github_repository" {
  description = "GitHub repository name (without org). Required when github_oidc_enabled."
  type        = string
  default     = ""

  validation {
    condition     = !var.github_oidc_enabled || can(regex("^[A-Za-z0-9_.-]+$", var.github_repository))
    error_message = "github_repository must be set when github_oidc_enabled is true."
  }
}

variable "github_entity_type" {
  description = "GitHub OIDC subject entity: environment, ref, or pull_request."
  type        = string
  default     = "environment"

  validation {
    condition     = contains(["environment", "ref", "pull_request"], var.github_entity_type)
    error_message = "github_entity_type must be environment, ref, or pull_request."
  }
}

variable "github_entity_name" {
  description = "Environment name or git ref (e.g. refs/heads/main). Unused for pull_request."
  type        = string
  default     = "dev"

  validation {
    condition     = var.github_entity_type == "pull_request" || length(trimspace(var.github_entity_name)) > 0
    error_message = "github_entity_name is required unless github_entity_type is pull_request."
  }
}

variable "federated_credential_name" {
  description = "Name of the federated identity credential resource."
  type        = string
  default     = "github-actions-oidc"

  validation {
    condition     = can(regex("^[a-zA-Z0-9][a-zA-Z0-9_-]{1,118}[a-zA-Z0-9]$", var.federated_credential_name))
    error_message = "federated_credential_name must be a valid Azure federated credential name."
  }
}

variable "tags" {
  description = "Tags applied to the identity."
  type        = map(string)
  default     = {}
}
