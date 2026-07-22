# ADR-004: Fault injection strategy

- **Status:** Accepted
- **Date:** 2026-07-22
- **Deciders:** OrderFlow portfolio owner (Dan Lewis); platform lead for this lab

## Context

SRE portfolio value comes from **demonstrable** failure handling: detect, mitigate, learn. Options:

1. **In-process / app knobs** (`payment-mock` latency/failure, worker crash scripts)
2. **Load + kubectl drills** (k6 profiles, pod kill, bad deploy)
3. **Chaos Mesh / Litmus** (powerful, heavier ops surface)

Required drill classes (lab scope): payment latency/fail, DB exhaustion, queue backlog, worker crashloop, bad deploy, stale config, partial disruption, AI latency/cost — plus related operational scenarios as scripts mature.

## Decision

Use the **smallest set** that covers required scenarios:

- **App-level fault injection** via `payment-mock` and controlled failure flags
- **k6** (or equivalent) load profiles: weekday, lunch, stadium surge (**simulated** traffic)
- **kubectl / scripted drills** under `deploy/chaos` and `scripts/drills`

**Defer** Chaos Mesh / Litmus unless a required drill cannot be shown otherwise. Document that deferral honestly.

## Consequences

**Positive**

- Fast to implement; easy to reason about in interviews.
- Failures stay tied to application semantics (payments, queue, deploy).
- Avoids running another control plane just to kill pods.

**Negative / trade-offs**

- Less “chaos engineering platform” branding — acceptable; judgment > tooling theater.
- Network-level or node-level chaos is limited without a chaos operator.

**Follow-ups**

- Phase 6: map each failure class to a reproducible script and runbook.
- One blameless postmortem with measured impact from a real drill in this lab.
