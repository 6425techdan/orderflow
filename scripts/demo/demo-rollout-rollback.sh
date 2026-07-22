#!/usr/bin/env bash
# Demo: roll a new order-api image tag, then roll back.
# LAB-ONLY — simulated rollout/rollback; human retains rollback authority.
set -euo pipefail

NAMESPACE="${ORDERFLOW_NAMESPACE:-orderflow}"
DEPLOY="${ORDERFLOW_DEPLOY:-order-api}"
CONTAINER="${ORDERFLOW_CONTAINER:-order-api}"
CANARY_IMAGE="${ORDERFLOW_CANARY_IMAGE:-orderflow/order-api:canary-sim}"
TIMEOUT="${ORDERFLOW_ROLLOUT_TIMEOUT:-180s}"

echo "==> OrderFlow demo rollout → rollback (lab)"
echo "    namespace=${NAMESPACE} deploy=${DEPLOY}"

if ! command -v kubectl >/dev/null 2>&1; then
  echo "error: kubectl is required" >&2
  exit 1
fi

echo "==> Baseline revision history"
kubectl -n "${NAMESPACE}" rollout history "deploy/${DEPLOY}"

CURRENT_IMAGE="$(kubectl -n "${NAMESPACE}" get "deploy/${DEPLOY}" -o jsonpath="{.spec.template.spec.containers[?(@.name=='${CONTAINER}')].image}")"
echo "    current image: ${CURRENT_IMAGE}"

echo "==> Rollout canary image: ${CANARY_IMAGE}"
kubectl -n "${NAMESPACE}" set image "deploy/${DEPLOY}" "${CONTAINER}=${CANARY_IMAGE}"
kubectl -n "${NAMESPACE}" rollout status "deploy/${DEPLOY}" --timeout="${TIMEOUT}" || {
  echo "warn: canary rollout did not become ready — proceeding to rollback" >&2
}

echo "==> Manual rollback authority: undoing deployment"
kubectl -n "${NAMESPACE}" rollout undo "deploy/${DEPLOY}"
kubectl -n "${NAMESPACE}" rollout status "deploy/${DEPLOY}" --timeout="${TIMEOUT}"

RESTORED="$(kubectl -n "${NAMESPACE}" get "deploy/${DEPLOY}" -o jsonpath="{.spec.template.spec.containers[?(@.name=='${CONTAINER}')].image}")"
echo "==> Restored image: ${RESTORED}"
echo "==> Demo complete (lab). If Argo CD self-heal is enabled, pause sync or revert git to avoid drift."
echo "    See docs/runbooks/rollback.md and docs/runbooks/canary-simulation.md"
