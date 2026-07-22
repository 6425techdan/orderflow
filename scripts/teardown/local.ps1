# Teardown local OrderFlow lab resources (Compose). Does NOT touch Azure.
$ErrorActionPreference = "Continue"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $Root

Write-Host "OrderFlow local teardown (Compose). Simulated lab only — no cloud destroy."

if (Get-Command docker -ErrorAction SilentlyContinue) {
  docker compose -f deploy/compose/docker-compose.yml down -v --remove-orphans
} else {
  Write-Warning "docker not found; skip compose down"
}

if ($env:ORDERFLOW_DELETE_KIND -eq "1" -and (Get-Command kind -ErrorAction SilentlyContinue)) {
  $cluster = if ($env:ORDERFLOW_KIND_CLUSTER) { $env:ORDERFLOW_KIND_CLUSTER } else { "orderflow" }
  Write-Host "Deleting kind cluster $cluster (ORDERFLOW_DELETE_KIND=1)"
  kind delete cluster --name $cluster
} else {
  Write-Host "Skipping kind delete (set ORDERFLOW_DELETE_KIND=1 to enable)."
}

Write-Host "Done. Azure/Terraform were not modified."
