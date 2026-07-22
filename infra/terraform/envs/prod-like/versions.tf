terraform {
  required_version = ">= 1.7"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }

  # ---------------------------------------------------------------------------
  # Remote state (azurerm) — COMMENTED until approved. Same rules as envs/dev.
  # Prefer Azure AD: use_azuread_auth = true. Never commit access keys.
  #
  # backend "azurerm" {
  #   resource_group_name  = "rg-orderflow-tfstate"
  #   storage_account_name = "storderflowtfstate"
  #   container_name       = "tfstate"
  #   key                  = "orderflow/prod-like.tfstate"
  #   use_azuread_auth     = true
  # }
  # ---------------------------------------------------------------------------
}
