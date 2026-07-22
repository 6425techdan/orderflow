# Demo: roll a new order-api image tag, then roll back.
# LAB-ONLY - simulated rollout/rollback; human retains rollback authority.
[CmdletBinding()]
param(
    [string]$Namespace = $(if ($env:ORDERFLOW_NAMESPACE) { $env:ORDERFLOW_NAMESPACE } else { "orderflow" }),
    [string]$Deploy = $(if ($env:ORDERFLOW_DEPLOY) { $env:ORDERFLOW_DEPLOY } else { "order-api" }),
    [string]$Container = $(if ($env:ORDERFLOW_CONTAINER) { $env:ORDERFLOW_CONTAINER } else { "order-api" }),
    [string]$CanaryImage = $(if ($env:ORDERFLOW_CANARY_IMAGE) { $env:ORDERFLOW_CANARY_IMAGE } else { "orderflow/order-api:canary-sim" }),
    [string]$Timeout = $(if ($env:ORDERFLOW_ROLLOUT_TIMEOUT) { $env:ORDERFLOW_ROLLOUT_TIMEOUT } else { "180s" })
)

$ErrorActionPreference = "Stop"

Write-Host "==> OrderFlow demo rollout -> rollback (lab)"
Write-Host "    namespace=$Namespace deploy=$Deploy"

if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
    throw "kubectl is required"
}

Write-Host "==> Baseline revision history"
kubectl -n $Namespace rollout history "deploy/$Deploy"

$jp = '{.spec.template.spec.containers[0].image}'
$currentImage = kubectl -n $Namespace get "deploy/$Deploy" -o "jsonpath=$jp"
Write-Host "    current image: $currentImage"

Write-Host "==> Rollout canary image: $CanaryImage"
kubectl -n $Namespace set image "deploy/$Deploy" "${Container}=$CanaryImage"
$rolloutOk = $true
try {
    kubectl -n $Namespace rollout status "deploy/$Deploy" --timeout=$Timeout
    if ($LASTEXITCODE -ne 0) { $rolloutOk = $false }
} catch {
    $rolloutOk = $false
}
if (-not $rolloutOk) {
    Write-Warning "canary rollout did not become ready - proceeding to rollback"
}

Write-Host "==> Manual rollback authority: undoing deployment"
kubectl -n $Namespace rollout undo "deploy/$Deploy"
kubectl -n $Namespace rollout status "deploy/$Deploy" --timeout=$Timeout

$restored = kubectl -n $Namespace get "deploy/$Deploy" -o "jsonpath=$jp"
Write-Host "==> Restored image: $restored"
Write-Host "==> Demo complete (lab). If Argo CD self-heal is enabled, pause sync or revert git to avoid drift."
Write-Host "    See docs/runbooks/rollback.md and docs/runbooks/canary-simulation.md"
