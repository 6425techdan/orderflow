# Bring up a local kind cluster and apply the OrderFlow local Kustomize overlay.
# LAB-ONLY — simulated reliability environment, not production.
[CmdletBinding()]
param(
    [string]$ClusterName = $(if ($env:ORDERFLOW_KIND_CLUSTER) { $env:ORDERFLOW_KIND_CLUSTER } else { "orderflow" }),
    [switch]$LoadImages
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$Overlay = Join-Path $Root "deploy\kustomize\overlays\local"
$KubeconfigOut = if ($env:ORDERFLOW_KUBECONFIG) {
    $env:ORDERFLOW_KUBECONFIG
} else {
    Join-Path $Root ".local\kind-$ClusterName.kubeconfig"
}

Write-Host "==> OrderFlow kind-up (lab)"
Write-Host "    cluster=$ClusterName"
Write-Host "    overlay=$Overlay"

if (-not (Get-Command kind -ErrorAction SilentlyContinue)) {
    throw "kind is required (https://kind.sigs.k8s.io/)"
}
if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
    throw "kubectl is required"
}

New-Item -ItemType Directory -Force -Path (Split-Path $KubeconfigOut) | Out-Null

$existing = @()
try {
    $existing = @(kind get clusters 2>$null)
} catch {
    $existing = @()
}
if ($existing -notcontains $ClusterName) {
    Write-Host "==> Creating kind cluster $ClusterName"
    kind create cluster --name $ClusterName --kubeconfig $KubeconfigOut
} else {
    Write-Host "==> kind cluster $ClusterName already exists"
    kind export kubeconfig --name $ClusterName --kubeconfig $KubeconfigOut
}

$env:KUBECONFIG = $KubeconfigOut

$shouldLoad = $LoadImages -or ($env:ORDERFLOW_LOAD_IMAGES -eq "1")
if ($shouldLoad) {
    Write-Host "==> Loading local images into kind"
    foreach ($img in @(
            "orderflow/order-api:local",
            "orderflow/order-worker:local",
            "orderflow/payment-mock:local"
        )) {
        docker image inspect $img 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            kind load docker-image $img --name $ClusterName
        } else {
            Write-Warning "image $img not found locally - skip load"
        }
    }
}

Write-Host "==> Applying Kustomize overlay (local)"
kubectl apply -k $Overlay

Write-Host "==> Waiting for core workloads"
kubectl -n orderflow rollout status deploy/postgres --timeout=180s
kubectl -n orderflow rollout status deploy/redis --timeout=180s
kubectl -n orderflow rollout status deploy/payment-mock --timeout=180s
kubectl -n orderflow rollout status deploy/order-api --timeout=180s
kubectl -n orderflow rollout status deploy/order-worker --timeout=180s

Write-Host "==> Done"
Write-Host "    `$env:KUBECONFIG = '$KubeconfigOut'"
Write-Host "    kubectl -n orderflow get pods"
Write-Host "Note: HPA may be inactive until metrics-server is installed. Postgres/Redis are lab-only single pods."
