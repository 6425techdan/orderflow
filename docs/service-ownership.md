# Service Ownership

Solo portfolio lab — “teams” are logical boundaries for interview clarity.

| Field | Value |
|---|---|
| Primary owner | Dan Lewis |
| Backup | None — freeze demos / run teardown if unavailable |
| Escalation | N/A for public demos; Azure STOP gates still apply |

## Service map

| Service | Path | Runbooks / notes |
|---|---|---|
| order-api | `apps/order-api` | latency, availability burn |
| order-worker | `apps/order-worker` | queue, payment |
| payment-mock | `apps/payment-mock` | [payment-dependency.md](runbooks/payment-dependency.md) |
| incident-assistant | `apps/incident-assistant` | advisory only |
| Platform | `deploy/` | rollback, gitops-drift, canary |
| Infra (Terraform) | `infra/terraform/` | **STOP before apply** — [oidc-azure.md](oidc-azure.md) |

## Interfaces

- HTTP `/v1/orders` (order-api)
- payment-mock `/v1/payments` + `/v1/faults`
- Redis Streams `orders` / group `order-workers`
- Assistant CLI + `/v1/analyze` (no successful execute)

Do not invent fake 24/7 on-call rotations.
