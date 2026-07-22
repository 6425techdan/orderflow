# AGENTS.md — OrderFlow

## Mission

**6425 Reliability Lab OrderFlow portfolio** — a local-first reliability and order-flow lab for demonstrating SLOs, probes, failure drills, and honest engineering practices.

## Hard constraints

1. **Local-first** — Prefer local tooling (kind, Docker, local stacks). Do not assume cloud.
2. **No paid Azure without approval** — Do not provision, enable, or spend on paid Azure (or other paid cloud) without explicit human approval.
3. **No secrets** — Never commit secrets, credentials, API keys, or kubeconfigs with credentials. Use placeholders and env templates only.
4. **No autonomous AI infra changes** — Agents must not autonomously change infrastructure, cluster topology, CI billing, or cloud accounts. Propose; wait for approval.
5. **Honest simulated scale** — Label demos and load as simulated. Do not claim production scale, real market volume, or unverified capacity.
6. **Plan before large changes** — Multi-file, architectural, or infra work requires a short plan and inspection of existing code first.
7. **Tests with behavioral changes** — Behavior changes ship with tests (or an explicit, justified exception).
8. **No fabricated results** — Never invent test output, metrics, drill outcomes, or “passing” claims. Report only what was actually run and observed.

## Operating notes

- Inspect the repo before proposing changes.
- Keep docs aligned with implementation; distinguish facts, assumptions, and recommendations.
- Prefer smallest credible change that meets the objective.
