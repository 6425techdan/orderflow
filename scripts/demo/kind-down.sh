#!/usr/bin/env bash
# Tear down the OrderFlow kind cluster.
# LAB-ONLY — destroys the local demo cluster named by ORDERFLOW_KIND_CLUSTER (default: orderflow).
set -euo pipefail

CLUSTER_NAME="${ORDERFLOW_KIND_CLUSTER:-orderflow}"

echo "==> OrderFlow kind-down (lab)"
echo "    cluster=${CLUSTER_NAME}"

if ! command -v kind >/dev/null 2>&1; then
  echo "error: kind is required" >&2
  exit 1
fi

if kind get clusters 2>/dev/null | grep -qx "${CLUSTER_NAME}"; then
  kind delete cluster --name "${CLUSTER_NAME}"
  echo "==> Deleted kind cluster ${CLUSTER_NAME}"
else
  echo "==> kind cluster ${CLUSTER_NAME} not found — nothing to delete"
fi

echo "Note: kubeconfig under .local/ is left in place; remove manually if desired."
