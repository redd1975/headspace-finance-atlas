# Mandatory Headspace / Xpace architecture instructions

Before architecture-affecting work, read **[redd1975/SAAS](https://github.com/redd1975/SAAS/blob/70e2d49b131f095cf8fcf01d48e84fff793d614e/architecture/README.md)**, the canonical architecture repository. The exact reviewed revision and decision digest are in `.architecture-policy.json`. Read the applicable `HSX-001`–`HSX-101` answers, governance and open issues at that revision. Do not maintain a competing decision register in this repository.

- These are Owner-confirmed architecture policies, not evidence of completed production features or permission to deploy/migrate. Keep work on branches and obtain the required individual Owner merge/release approval. Existing app guards and runbooks still apply.
- Preserve tenant/company/branch boundaries, permanent source IDs, verified legacy crosswalks, FIN09 accounting keys, Personal privacy, historical ledger entries and evidence. Never infer a match from a name, amount, branch label or email alone.
- Use People staff identity/permissions for the approved Headspace target; keep the Xpace-root-auth conflict explicit until resolved. QR credentials are revocable credentials, not replacement employee IDs.
- Source apps own business records and transactional outboxes; Xpace routes events. Do not write another app's database or duplicate financial effects during retries or reconciliation.
- Follow current Owner instructions, scoped approved decisions and applicable existing safeguards. Identify specific contradictions rather than silently rewriting either side. Do not treat assistant suggestions or unanswered Q102 as approved policy.
- Implement the shortest safe functional slice, make it reviewable in preview, run meaningful checks for the change, and continue through completion. Do not re-ask settled design questions. Independent work can continue while a real dependent decision is pending.
- Every PR must state `Architecture-Revision`, applicable `Architecture-Decisions` and `Architecture-Impact` (see template), plus validation and any unresolved boundary. CI validates adoption metadata; it does not certify semantic compliance or authenticate Owner approval.
- Read existing `CLAUDE.md`, nested agent instructions and deployment rules. Never weaken existing Loyverse write guards or mark a production identity mapping verified from this policy record alone.

If the private canonical source cannot be read, obtain authorized access; report that affected architectural work is blocked. Do not guess its content or copy private financial/identity decisions into public repositories. Future apps must adopt the starter files from the same canonical repository before implementation.
