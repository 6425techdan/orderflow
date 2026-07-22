terraform {
  required_version = ">= 1.7"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }

  # ---------------------------------------------------------------------------
  # Remote state (azurerm) — COMMENTED until storage-state exists and apply is
  # explicitly approved. Do NOT uncomment without:
  #   1) Reading docs/azure-deployment-plan.md and docs/cost-model.md
  #   2) Explicit human approval for paid Azure
  #   3) Creating the state storage account (bootstrap) outside this stack or via
  #      a one-time local-state apply of module storage-state only
  #
  # Instructions:
  #   - Copy values from a non-committed backend.hcl or CI OIDC-authenticated run
  #   - Prefer Azure AD auth: use_azuread_auth = true (no access keys in files)
  #   - Never commit access keys, SAS tokens, or service principal secrets
  #
  # backend "azurerm" {
  #   resource_group_name  = "rg-orderflow-tfstate"   # bootstrap RG
  #   storage_account_name = "storderflowtfstate"     # globally unique
  #   container_name       = "tfstate"
  #   key                  = "orderflow/dev.tfstate"
  #   use_azuread_auth     = true
  # }
  # ---------------------------------------------------------------------------
}
