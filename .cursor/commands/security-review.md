# Security Review

Perform a security review of the current change or uncommitted/branch diff.

1. Scan for secrets, credentials, tokens, private keys, and authenticated kubeconfigs.
2. Check cloud/spend exposure, public endpoints, and destructive ops without approval.
3. Review dependency/supply-chain changes and weakened security controls.
4. Output: STOP-gate items first, then other findings and remediations. Do not commit secrets or fabricate scan results.
