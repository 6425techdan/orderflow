locals {
  # Placeholder subject templates for GitHub OIDC — replace org/repo/entity via variables.
  # See: https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect
  github_subject = (
    var.github_entity_type == "environment" ? "repo:${var.github_organization}/${var.github_repository}:environment:${var.github_entity_name}" :
    var.github_entity_type == "ref" ? "repo:${var.github_organization}/${var.github_repository}:ref:${var.github_entity_name}" :
    "repo:${var.github_organization}/${var.github_repository}:pull_request"
  )
}

resource "azurerm_user_assigned_identity" "this" {
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name
  tags                = var.tags
}

# Federated credential for GitHub Actions OIDC — no long-lived client secrets.
resource "azurerm_federated_identity_credential" "github" {
  count = var.github_oidc_enabled ? 1 : 0

  name                = var.federated_credential_name
  resource_group_name = var.resource_group_name
  parent_id           = azurerm_user_assigned_identity.this.id
  audience            = ["api://AzureADTokenExchange"]
  issuer              = "https://token.actions.githubusercontent.com"
  subject             = local.github_subject
}
