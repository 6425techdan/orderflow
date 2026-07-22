# Security

## Reporting

If you discover a vulnerability or accidental secret exposure in OrderFlow:

1. **Do not** open a public issue that includes secrets or exploit detail.
2. Notify the maintainer privately (repository owner / Dan Lewis) with impact, reproduction steps, and suggested remediation if known.
3. Rotate any exposed credentials immediately and treat the exposure as an incident.

## Secrets policy

- Never commit secrets: API keys, tokens, passwords, private keys, connection strings with credentials, or authenticated kubeconfigs.
- Use environment variables and ignored local files (see `.gitignore`). Prefer `.env.example` with placeholders.
- If a secret is committed, treat it as compromised: rotate, purge from history if needed (with approval), and document the incident.

## STOP gates (require explicit human approval)

Stop and ask before:

| Gate | Examples |
|------|----------|
| Paid / cloud spend | Paid Azure or other billed cloud resources |
| Destructive ops | Cluster wipe, irreversible destroy, force-push to main, mass data delete |
| Security control weakening | Disabling checks, broad public exposure, unpinned risky deps without review |
| Autonomous infra changes | Agents changing live infra, CI billing, or account settings without approval |

## Local-first default

Prefer local stacks (kind, Docker, local observability). Label simulated scale and drills honestly. Do not claim production hardening that is not implemented.
