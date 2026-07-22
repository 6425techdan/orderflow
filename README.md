# 6425 Reliability Lab: OrderFlow

Fictional distributed restaurant ordering platform for demonstrating contemporary SRE and platform-engineering practices.

> **Simulated scale only.** References to 300 restaurant locations, lunch rushes, and stadium surges are load-generator scenarios. This repository does not contain proprietary employer systems, configurations, or transaction data.

## Quick start (local default)

```bash
make install
make test
make up
make e2e
```

- API: http://localhost:8080/healthz
- Grafana: http://localhost:3000 (anonymous viewer enabled for lab)
- Prometheus: http://localhost:9090

Teardown: `make down`

## Architecture

See [docs/architecture.md](docs/architecture.md). Local path uses Docker Compose + OpenTelemetry + Prometheus/Grafana/Loki/Tempo. Optional Azure AKS is plan-only until explicit cost approval.

## Reliability goals

Defined in [docs/slo-and-error-budget.md](docs/slo-and-error-budget.md). Error budgets gate release decisions in lab drills.

Postmortem example: [docs/incidents/INC-2026-07-lab-payment-surge.md](docs/incidents/INC-2026-07-lab-payment-surge.md).

## What AI did and did not do

- **Did:** optional advisory incident hypotheses from sanitized fixtures (Phase 7).
- **Did not:** apply Terraform, mutate Kubernetes, approve deploys, or access secrets.

See [docs/ai-safety-and-verification.md](docs/ai-safety-and-verification.md).

## Prerequisites

- Python 3.9+ (3.12 recommended; Compose images use 3.12)
- Docker Desktop / Engine for `make up` (optional if you only run unit/eval tests)
- kind + kubectl for local Kubernetes demos

```bash
python -m venv .venv
# Windows: .\.venv\Scripts\activate
# Unix: source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

## Documentation map

| Doc | Purpose |
|---|---|
| [docs/roadmap.md](docs/roadmap.md) | Phased delivery |
| [docs/runbooks/](docs/runbooks/) | Operational runbooks |
| [docs/incidents/](docs/incidents/) | Blameless postmortems |
| [docs/adr/](docs/adr/) | Architecture decisions |
| [docs/interview-walkthrough.md](docs/interview-walkthrough.md) | Demo script for interviews |
| [docs/cost-model.md](docs/cost-model.md) | Local vs Azure cost estimates |
| [docs/threat-model.md](docs/threat-model.md) | Threat model |

## STOP gates

No paid Azure resources, `terraform apply`, or destructive cloud actions without explicit human approval.
