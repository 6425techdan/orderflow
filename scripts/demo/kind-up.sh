#!/usr/bin/env bash
# Bring up a local kind cluster and apply the OrderFlow local Kustomize overlay.
# LAB-ONLY — simulated reliability environment, not production.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CLUSTER_NAME="${ORDERFLOW_KIND_CLUSTER:-orderflow}"
OVERLAY="${ROOT}/deploy/kustomize/overlays/local"
KUBECONFIG_OUT="${ORDERFLOW_KUBECONFIG:-${ROOT}/.local/kind-${CLUSTER_NAME}.kubeconfig}"

echo "==> OrderFlow kind-up (lab)"
echo "    cluster=${CLUSTER_NAME}"
echo "    overlay=${OVERLAY}"

if ! command -v kind >/dev/null 2>&1; then
  echo "error: kind is required (https://kind.sigs.k8s.io/)" >&2
  exit 1
fi
if ! command -v kubectl >/dev/null 2>&1; then
  echo "error: kubectl is required" >&2
  exit 1
fi

mkdir -p "$(dirname "${KUBECONFIG_OUT}")"

if ! kind get clusters 2>/dev/null | grep -qx "${CLUSTER_NAME}"; then
  echo "==> Creating kind cluster ${CLUSTER_NAME}"
  kind create cluster --name "${CLUSTER_NAME}" --kubeconfig "${KUBECONFIG_OUT}"
else
  echo "==> kind cluster ${CLUSTER_NAME} already exists"
  kind export kubeconfig --name "${CLUSTER_NAME}" --kubeconfig "${KUBECONFIG_OUT}"
fi

export KUBECONFIG="${KUBECONFIG_OUT}"

# Optionally load locally built images into kind (tags must match local overlay).
if [[ "${ORDERFLOW_LOAD_IMAGES:-0}" == "1" ]]; then
  echo "==> Loading local images into kind"
  for img in orderflow/order-api:local orderflow/order-worker:local orderflow/payment-mock:local; do
    if docker image inspect "${img}" >/dev/null 2>&1; then
      kind load docker-image "${img}" --name "${CLUSTER_NAME}"
    else
      echo "warn: image ${img} not found locally — skip load" >&2
    fi
  done
fi

echo "==> Applying Kustomize overlay (local)"
kubectl apply -k "${OVERLAY}"

echo "==> Waiting for core workloads"
kubectl -n orderflow rollout status deploy/postgres --timeout=180s || true
kubectl -n orderflow rollout status deploy/redis --timeout=180s || true
kubectl -n orderflow rollout status deploy/payment-mock --timeout=180s || true
kubectl -n orderflow rollout status deploy/order-api --timeout=180s || true
kubectl -n orderflow rollout status deploy/order-worker --timeout=180s || true

echo "==> Done"
echo "    export KUBECONFIG=${KUBECONFIG_OUT}"
echo "    kubectl -n orderflow get pods"
echo "Note: HPA may be inactive until metrics-server is installed. Postgres/Redis are lab-only single pods."
