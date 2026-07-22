# ADR-007: Image tagging, provenance, and promotion

- **Status:** Accepted
- **Date:** 2026-07-22
- **Deciders:** OrderFlow portfolio owner (Dan Lewis); platform lead for this lab

## Context

Portfolio CI often stops at “docker build pushed :latest,” which is a poor supply-chain story. We need a promotion model that is honest about local vs registry and does not require Azure on day one.

## Decision

1. **Never rely on `:latest` for demos that claim reproducibility.** Prefer immutable tags (git SHA) and/or **digest** references in deploy manifests where practical.
2. CI builds images, runs **vuln scan**, produces **SBOM**, and records **provenance / attestations** as the toolchain allows (e.g. GitHub Actions attestations or documented equivalent).
3. Promotion path: build on PR/main → promote digest to staging overlay → prod-like requires **environment protection** / manual approval.
4. Local kind may load images directly (`kind load`) without ACR; ACR is optional Azure path under STOP gates.
5. Document how to verify image identity (digest) in the interview walkthrough when implemented.

## Consequences

**Positive**

- Aligns with modern secure software supply-chain expectations.
- Separates “built” from “deployed” with human gates for prod-like.
- Works with local-first (kind load) and optional ACR later.

**Negative / trade-offs**

- More CI complexity than a toy repo.
- Attestation tooling varies; document what is actually implemented vs aspirational.

**Follow-ups**

- Phase 5: wire scan/SBOM/provenance into workflows; pin actions by SHA.
- Keep `SECURITY.md` and runbooks updated with verification steps.
