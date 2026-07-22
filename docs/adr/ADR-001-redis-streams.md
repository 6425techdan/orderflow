# ADR-001: Redis Streams as the work queue

- **Status:** Accepted
- **Date:** 2026-07-22
- **Deciders:** OrderFlow portfolio owner (Dan Lewis); platform lead for this lab

## Context

OrderFlow needs an asynchronous path from `order-api` accept to `order-worker` processing so we can demonstrate backlog, queue age, retries, consumer groups, and idempotent handling under failure. Options considered:

1. **Redis Streams** (consumer groups)
2. **RabbitMQ** (classic portfolio choice)
3. **Kafka / managed bus** (overkill for this lab)
4. **Postgres-only “outbox poller”** (possible, weaker queue-age demos without extra work)

## Decision

Use **Redis Streams** with consumer groups as the primary work queue between `order-api` and `order-worker`.

Postgres remains the source of truth for order state. Redis carries work notifications and supports operational metrics (pending entries, lag/age approximations as implemented).

## Consequences

**Positive**

- Enough semantics for backlog, consumer groups, acknowledgment, and DLQ-style patterns without operating Kafka.
- Fits Compose and kind demos with a single Redis dependency already useful for other lab needs.
- Lower cognitive load than RabbitMQ for a one-person portfolio.

**Negative / trade-offs**

- Not a claim of “enterprise messaging” parity with RabbitMQ/Kafka.
- At-least-once delivery requires application-level idempotency (see ADR-005).
- Operational features (dead-letter, poison handling) are **application-designed**, not a full broker product feature set.

**Follow-ups**

- Document stream key naming, consumer group name, and ack/retry policy in Phase 1.
- Expose queue depth / age metrics for Grafana and drills.
