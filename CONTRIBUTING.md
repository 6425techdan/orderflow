# Contributing

Paved-road guide for OrderFlow (6425 Reliability Lab).

## Before you start

1. Read [AGENTS.md](./AGENTS.md) and [SECURITY.md](./SECURITY.md).
2. Prefer local-first workflows. Do not provision paid cloud without approval.
3. For multi-file or architectural work, sketch a short plan and inspect existing code first.

## Development expectations

- Match existing project structure and patterns.
- Behavior changes include tests (or a documented exception in the PR).
- Keep docs aligned with implementation; label facts vs assumptions vs recommendations.
- Never commit secrets, `.env` files, or authenticated kubeconfigs.
- Do not fabricate test, drill, or metric results.

## Pull requests

PRs should include:

- **Why** — problem and intent (not only a file list).
- **What** — scoped summary of the change.
- **How verified** — commands actually run and outcomes observed.
- **Risks / follow-ups** — honest gaps, simulated-scale caveats, open questions.

Use `/pre-pr-quality-check` before opening a PR when helpful.

## Review focus

Reviewers prioritize: correctness, local-first/security STOP gates, reliability/docs match, and evidence of verification.
