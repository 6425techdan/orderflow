# ADR-005: Idempotency and “exactly-once enough” order semantics

- **Status:** Accepted
- **Date:** 2026-07-22
- **Deciders:** OrderFlow portfolio owner (Dan Lewis); platform lead for this lab

## Context

Redis Streams and workers provide **at-least-once** delivery. Network retries and client repeats will happen in drills and real interviews’ whiteboard discussions. Claiming “exactly-once” end-to-end would be dishonest for this architecture.

We need:

- Safe client retries on submit
- Duplicate-safe worker processing (payment side effects must not double-charge in the mock sense)
- Clear language: **exactly-once enough** for portfolio demos, not a formal distributed transactions proof

## Decision

1. Clients supply an **idempotency key** on order submit; `order-api` stores and returns the same logical order on replay.
2. Worker processing is keyed by order identity (and/or stream message id mapping) so redelivery does not apply a second successful payment in `payment-mock` / order state machine.
3. Document delivery as **at-least-once + idempotent handlers**, not exactly-once messaging.

Postgres is the authority for “has this order already been accepted / paid / failed.”

## Consequences

**Positive**

- Matches how many production APIs actually behave.
- Gives concrete interview talking points (keys, unique constraints, ack after commit).
- Supports queue redelivery drills without corrupting demo state.

**Negative / trade-offs**

- Requires careful schema and tests; bugs here look like “flaky demos.”
- Cross-service exactly-once with a real PSP is out of scope (`payment-mock` only).

**Follow-ups**

- Phase 1: unique constraints + tests for duplicate submit and duplicate consume.
- Metrics for duplicate detection vs new accepts.
