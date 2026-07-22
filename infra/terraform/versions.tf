# Root configuration for repo-level `terraform test` / tooling.
# Environment stacks live under envs/dev and envs/prod-like — do not apply from here.

terraform {
  required_version = ">= 1.7"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
  # No credentials in code — use Azure CLI / ARM_* / OIDC at runtime.
}
