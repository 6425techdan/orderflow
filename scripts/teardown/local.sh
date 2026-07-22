#!/usr/bin/env bash
# Teardown local OrderFlow lab resources (Compose). Does NOT touch Azure.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "OrderFlow local teardown (Compose). Simulated lab only — no cloud destroy."

if command -v docker >/dev/null 2>&1; then
  docker compose -f deploy/compose/docker-compose.yml down -v --remove-orphans || true
else
  echo "docker not found; skip compose down" >&2
fi

if [[ "${ORDERFLOW_DELETE_KIND:-0}" == "1" ]] && command -v kind >/dev/null 2>&1; then
  CLUSTER="${ORDERFLOW_KIND_CLUSTER:-orderflow}"
  echo "Deleting kind cluster ${CLUSTER} (ORDERFLOW_DELETE_KIND=1)"
  kind delete cluster --name "${CLUSTER}" || true
else
  echo "Skipping kind delete (set ORDERFLOW_DELETE_KIND=1 to enable)."
fi

echo "Done. Azure/Terraform were not modified."
