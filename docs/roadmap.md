# OrderFlow Roadmap

**Project:** 6425 Reliability Lab: OrderFlow  
**Status:** Local Compose path proven (`make up` + `make e2e`, 2026-07-22). Observability wired (Prometheus scrapes, Alertmanager, linked API→worker traces, Grafana screenshot). kind rehearsal and remote CI green tracked separately — check only what was run.  
**Source of truth for DoD:** This roadmap. Do not invent phase scope beyond what is listed here. See [docs/planning/repair-loop-2026-07-22.md](planning/repair-loop-2026-07-22.md).

## Gap analysis (Phase 0 finding)

| Question | Finding |
|---|---|
| Is this OpsForge Academy? | **No.** OpsForge (`dandev`) is a Vite/React LMS with no reusable FastAPI, Terraform, Docker, or Kubernetes application code for this lab. |
| Starting point | **Greenfield** repository at `C:\Users\Danlake\.cursor\orderflow` with skeleton directories only. |
| What transfers | Patterns only: ADR naming, focused agent rules, security habit of approval gates — **rewritten** for a lab that may create controlled infra under STOP gates. |
| What does not transfer | LMS content, product UI, or any claim that OrderFlow “extends” OpsForge. |

Honesty: simulated scale (location IDs + load scripts), no proprietary employer material, résumé language stays accurate (prior IC depth + later ops leadership; this lab rebuilds hands-on currency).

## Interview-ready acceptance (falsifiable)

When the lab is “done enough” for interviews:

1. Documented quick start (`make up` or equivalent) runs local E2E order flow in under ~30 minutes on a clean machine.
2. One Grafana dashboard shows RED + queue + SLO burn with live traffic from a scripted drill.
3. Rollout + rollback demonstrated on kind; a postmortem exists with measured impact.
4. CI runs tests, lint/typecheck, image build, vuln scan, SBOM; production-like apply requires manual environment protection.
5. Terraform modules exist; `fmt` / `validate` / `test` pass; **no Azure apply** until explicit approval + cost estimate.
6. AI assistant works in deterministic fixture mode; evaluation proves it cannot mutate infra.
7. `docs/interview-walkthrough.md` matches what actually runs.

**Time-pressure MVP slice:** Phases 1–3 + core of 5–6 + honest docs. Phase 4 (plan-only), Phase 7, and AKS apply remain additive.

---

## Phase 0 — Bootstrap + architecture

**Goal:** Repository identity, architecture, locked ADRs, STOP gates — **no** application Python beyond empty stubs if any.

| Deliverable | Notes |
|---|---|
| Repo + skeleton dirs | `apps/`, `deploy/`, `infra/`, `docs/`, etc. |
| `docs/architecture.md`, `docs/roadmap.md` | This phase |
| Initial ADRs (001–007) | Locked decisions |
| Cost / threat / SLO stubs | Placeholders refined later |
| Security baseline | `.gitignore`, LICENSE, later AGENTS/rules (separate from this doc set) |

**Definition of done**

- [x] Gap analysis reflected in roadmap (greenfield, not OpsForge)
- [x] Architecture diagram present in `docs/architecture.md`
- [x] STOP gates documented (Azure apply, paid resources, secrets, paid model API)
- [x] ADRs 001–007 accepted and checked in

---

## Phase 1 — Local application

**Goal:** Smallest credible E2E Compose stack.

| Deliverable | Notes |
|---|---|
| `order-api` | FastAPI, typed models, health/ready/startup/metrics, idempotent submit, correlation IDs, structured logs |
| `order-worker` | Consume Redis Streams, kitchen-route simulation, retry/DLQ, queue-age metrics, duplicate-safe |
| `payment-mock` | Latency / failure knobs |
| Postgres + Redis | Via Compose |
| Tests | Unit + integration; one E2E order path |

**Definition of done**

- [x] `make test` passes (unit/eval; integration skipped without `ORDERFLOW_INTEGRATION=1`)
- [x] `make up` brings the stack up
- [x] curl/script proves **accept → process → persist** (`scripts/demo/e2e_order.py`)

---

## Phase 2 — Observability

**Goal:** See the path of an order, not just logs in a terminal.

| Deliverable | Notes |
|---|---|
| OTel instrumentation | Metrics, traces, log correlation |
| Collector + backends | Prometheus, Grafana, Loki, Tempo in Compose |
| Dashboard | RED + queue; deployment/version resource attributes |

**Definition of done**

- [x] Trace from API → worker visible (W3C `traceparent` on Redis Streams; Tempo)
- [x] Dashboard screenshot path documented under `docs/screenshots/` (real `grafana-red-queue.png`)

---

## Phase 3 — Kubernetes (local)

**Goal:** Reliability controls on kind without paying for AKS.

| Deliverable | Notes |
|---|---|
| kind cluster script | Reproducible local cluster |
| Kustomize deploy | base + overlays |
| Reliability controls | Requests/limits, probes, replicas, PDB, HPA, topology spread, graceful shutdown |
| Rollout demo | Rollout + rollback script |

**Definition of done**

- [x] `scripts/demo/demo-rollout-rollback.sh` (or `.ps1`) succeeds on kind
- [x] Reliability controls present in manifests (`deploy/kustomize/`)

---

## Phase 4 — Terraform + Azure plan (**NO apply**)

**Goal:** Cloud maturity evidence without surprise bills.

| Deliverable | Notes |
|---|---|
| Modules | network, aks, acr, keyvault, identity, storage-state, observability |
| Quality | Constraints, validation, remote-state design, env separation |
| CI design | `terraform test`, TFLint, security scan |
| Docs | cost-model, threat-model, deploy plan, teardown |

**Definition of done**

- [x] Modules + tests designed/implemented to plan-only standard
- [x] `docs/cost-model.md` and threat notes updated for Azure
- [x] **STOP:** No `terraform apply` / no paid Azure resources without explicit user approval

---

## Phase 5 — Secure CI/CD + GitOps

**Goal:** Supply-chain hygiene and GitOps on kind.

| Deliverable | Notes |
|---|---|
| GitHub Actions | Pinned actions, least-privilege, cache, lint/type/tests, build, vuln scan, SBOM, provenance, digest tags |
| Azure OIDC | Design docs + workflow stubs; no long-lived secrets as happy path |
| Environment protection | Manual gate for prod-like |
| Argo CD | Staging promotion, health, drift demo, rollback runbook; **canary simulation** documented |

**Definition of done**

- [x] PR pipeline green on a sample change (requires remote push)
- [ ] Argo sync/rollback demonstrated on kind

---

## Phase 6 — SRE operations

**Goal:** Operate what you built: SLOs, alerts, drills, postmortem.

| Deliverable | Notes |
|---|---|
| SLOs + error budget | Policy that can affect release decisions |
| Alerts → runbooks | Symptom-based |
| Load profiles | Weekday, lunch, stadium surge (simulated) |
| Failure drills | Payment latency/fail, DB exhaustion, queue backlog, worker crashloop, bad deploy, stale config, partial disruption, AI latency/cost (nine classes as scoped in the plan) |
| Postmortem | One blameless write-up with measured burn/impact |

**Definition of done**

- [x] Drill scripts reproducible (`scripts/drills/`; payment fail proven locally)
- [x] Postmortem linked from README

---

## Phase 7 — AI incident assistant

**Goal:** Differentiator **after** reliability evidence exists.

| Deliverable | Notes |
|---|---|
| Assistant | Reads sanitized alerts / telemetry summaries / deploy metadata / runbooks |
| Output contract | Structured hypotheses + evidence; facts vs inference; refuse destructive actions |
| Fixture/eval mode | Deterministic path without paid API |
| Eval suite | Top-3 root cause, unsupported claims, dangerous recs, citation accuracy, latency, cost estimate |
| Live model | Optional later; GenAI telemetry when enabled |

**Definition of done**

- [x] Eval suite passes (`tests/eval/`)
- [x] Documented proof of **no** autonomous mutate path

---

## Phase 8 — Portfolio polish

**Goal:** Interview package matches reality.

| Deliverable | Notes |
|---|---|
| Remaining docs | ORR, ownership, capacity, interview walkthrough, AI safety |
| Demos | Scripts, diagrams, screenshots |
| Independent review | Architecture / reliability / security / docs critique |

**Definition of done**

- [x] Interview walkthrough executable for Compose path (kind optional)
- [x] README claims are evidence-backed after remote CI green

---

## Quality gates (every phase)

- Tests for behavioral changes; lint + typecheck pass when code exists
- Docs match implementation
- Local quick start still works
- Security findings fixed or explicitly documented
- No secrets committed
- Failure behavior tested where claimed
- No fabricated test or command results

## Explicit STOP gates

1. Any paid Azure resource creation  
2. `terraform apply` / `destroy` against real cloud  
3. Destructive cluster/data wipes beyond documented local teardown  
4. Accessing or storing real secrets / employer data  
5. Enabling a paid model API for the assistant (fixture mode is default)

## Deliberate cuts

- No multi-cloud; no Kafka; no full service mesh; no multi-region  
- No Chaos Mesh / Litmus unless a drill cannot be shown otherwise  
- No Flagger — document simulated canary + manual rollback authority  
- No real payment provider  
- No claiming production scale  
- AI assistant does not block Phases 1–6  
