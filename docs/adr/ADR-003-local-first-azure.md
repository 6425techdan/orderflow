# ADR-003: Local-first runtime, Azure optional

- **Status:** Accepted
- **Date:** 2026-07-22
- **Deciders:** OrderFlow portfolio owner (Dan Lewis); platform lead for this lab

## Context

Dan’s background includes Azure / AKS, which makes Azure-first modules attractive for résumé alignment. Uncontrolled cloud spend and surprise applies are unacceptable for a personal lab. Options:

1. **Azure-first** — build against AKS from day one  
2. **Local-first** — Compose → kind as default; Azure modules plan-only until approved  
3. **Multi-cloud** — rejected as boil-the-ocean  

## Decision

**Local-first, Azure-optional.**

- Default runtime: Docker Compose, then kind.
- Terraform modules target Azure (AKS, ACR, Key Vault, identity, network, state storage, observability hooks) for interview depth.
- **No** `terraform apply`, **no** paid Azure resources, and **no** destroy against real subscriptions without explicit human approval and an updated [cost model](../cost-model.md).

## Consequences

**Positive**

- Interview demos remain reproducible offline / near $0.
- Terraform quality (modules, tests, validation) can still be shown via plan/validate/test.
- Aligns with prior AKS experience without pretending AKS is required to run the lab.

**Negative / trade-offs**

- “We run on AKS in prod” is **not** a claim until apply is approved and evidenced.
- Local kind ≠ managed control plane; document gaps (ingress, identity, storage classes).

**Follow-ups**

- Keep STOP gates in architecture, roadmap, AGENTS/rules, and cost model synchronized.
- Phase 4: modules + tests; still plan-only by default.
