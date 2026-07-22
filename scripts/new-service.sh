#!/usr/bin/env bash
# Golden path: scaffold notes for a new OrderFlow-style service.
set -euo pipefail
NAME="${1:-}"
if [[ -z "$NAME" ]]; then
  echo "Usage: $0 <service-name>"
  exit 1
fi
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "Paved road for service '$NAME':"
echo "  1. Create apps/$NAME with FastAPI/worker pattern from order-api"
echo "  2. Add deploy/kustomize/base/${NAME}-deployment.yaml (probes, resources, PDB)"
echo "  3. Export RED metrics + OTel resource attributes"
echo "  4. Add runbook under docs/runbooks/"
echo "  5. Wire CI job and image name orderflow/${NAME}"
echo "See CONTRIBUTING.md for PR expectations."
mkdir -p "$ROOT/apps/$NAME"
echo "# $NAME" > "$ROOT/apps/$NAME/README.md"
echo "Created apps/$NAME/README.md stub"
