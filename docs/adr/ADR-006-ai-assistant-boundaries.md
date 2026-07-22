# ADR-006: AI incident assistant boundaries

- **Status:** Accepted
- **Date:** 2026-07-22
- **Deciders:** OrderFlow portfolio owner (Dan Lewis); platform lead for this lab

## Context

An AI incident assistant is a market differentiator only if it shows **judgment and safety**, not autonomous ops theater. Risks: hallucinated root causes, unsafe “run this kubectl delete” advice, surprise API spend, and blocking core SRE evidence (Phases 1–6).

## Decision

1. Build the assistant in **Phase 7**, after reliability evidence exists.
2. **Advisory only:** structured hypotheses, evidence citations, facts vs inference. A human approver is required for any action.
3. **No autonomous mutate path** — no apply, destroy, scale, delete, or secret access from the assistant.
4. Default mode: **deterministic fixtures / evals** without a paid model API.
5. Inputs must be **sanitized** summaries (alerts, telemetry digests, deploy metadata, runbook text) — not raw secrets or employer data.
6. Enabling a paid model API is an explicit **STOP gate**.

Eval suite must measure (at minimum): top-3 root-cause usefulness, unsupported claims, dangerous recommendations, citation accuracy, latency, and estimated cost when a live model is used.

## Consequences

**Positive**

- Interview story: trust vs verify, not “Copilot for prod.”
- Lab remains runnable offline.
- Clear security boundary for reviewers.

**Negative / trade-offs**

- Less “wow” automation; that is intentional.
- Fixture mode must stay green even if live model is never enabled.

**Follow-ups**

- `docs/ai-safety-and-verification.md` expanded in Phase 7/8.
- Proof artifact: architecture or test showing absence of mutate tools/credentials in the assistant runtime.
