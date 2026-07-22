# Simple Terraform test for network module variable validation / plan shape.
# Run from infra/terraform:
#   terraform test
#
# Requires Terraform >= 1.7. Does not apply paid Azure resources when using
# plan/applyless unit assertions below. Provider auth is not required for
# variable-only checks; resource plan checks need a configured Azure provider.

run "network_name_prefix_valid" {
  command = plan

  module {
    source = "./modules/network"
  }

  variables {
    name_prefix             = "of-dev"
    location                = "eastus"
    resource_group_name     = "rg-orderflow-test"
    vnet_address_space      = ["10.10.0.0/16"]
    aks_subnet_prefix       = "10.10.0.0/22"
    endpoints_subnet_prefix = "10.10.4.0/24"
    tags = {
      project = "orderflow"
      purpose = "tftest"
    }
  }

  assert {
    condition     = azurerm_subnet.aks.name == "of-dev-snet-aks"
    error_message = "AKS subnet name should follow name_prefix convention."
  }

  assert {
    condition     = azurerm_subnet.endpoints.name == "of-dev-snet-endpoints"
    error_message = "Endpoints subnet name should follow name_prefix convention."
  }

  assert {
    condition     = azurerm_virtual_network.this.address_space[0] == "10.10.0.0/16"
    error_message = "VNet address space should match input."
  }
}

run "network_rejects_bad_prefix" {
  command = plan

  module {
    source = "./modules/network"
  }

  variables {
    name_prefix         = "BAD"
    location            = "eastus"
    resource_group_name = "rg-orderflow-test"
  }

  expect_failures = [
    var.name_prefix,
  ]
}
