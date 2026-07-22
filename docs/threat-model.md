# Threat Model

Informal STRIDE-oriented notes for this portfolio lab — **not** a formal audit.

## Scope

In: app services, Compose/kind, optional Azure modules, CI/GitOps, incident-assistant.  
Out: real POS/PSP, employer systems, internet-scale multi-tenant abuse.

## Assets

Order records (fictional), Redis payloads, CI OIDC identities, container images, telemetry (sanitize before AI).

## Trust boundaries

Client→API; services→Postgres/Redis; worker→payment-mock; CI→registry; human→terraform apply; assistant→sanitized telemetry (advisory).

## Top risks

| ID | Risk | Mitigation |
|---|---|---|
| T1 | Secrets in git/logs | `.gitignore`, `.env.example`, redaction |
| T2 | Poison queue / replay | Validation, DLQ, idempotency |
| T3 | Vulnerable images | Trivy + SBOM in `supply-chain.yml` |
| T4 | Accidental cloud spend | STOP gates, cost model, teardown |
| T5 | AI destructive advice | Advisory-only; evals; execute refuses |
| T6 | Mutable Action tags | Pin Actions to full commit SHAs |
| T7 | Local dashboard exposure | Bind wisely; no public expose by default |

## Non-claims

Not a pen test, PCI attestation, or “secure by default” production guarantee. Revisit before Azure apply or public exposure.
