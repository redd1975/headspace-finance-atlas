# Architecture source and adoption

The single architecture authority is **[redd1975/SAAS](https://github.com/redd1975/SAAS/blob/70e2d49b131f095cf8fcf01d48e84fff793d614e/architecture/README.md)**. This file is a pointer, not a copy of the policy register.

Read the reviewed revision in `.architecture-policy.json`, then `architecture/GOVERNANCE.md`, `architecture/v1/OWNER-QA.md` and `architecture/OPEN-ISSUES.md` at that same revision. Retain the existing source identifiers and guarded interfaces. Authoritative architecture adoption does not certify production implementation.

## This repository

Repository: `redd1975/headspace-finance-atlas`.
Scope: Public development Atlas; neutral policy pointers only, no private policy publication.

The rollout is a branch/PR change until Owner-approved merge. No production settings, accounts or data are changed by it. Private source read permission is required for agents working against the policy.

## PR acknowledgment

```
Architecture-Revision: 70e2d49b131f095cf8fcf01d48e84fff793d614e
Architecture-Decisions: HSX-065, HSX-066, HSX-067, HSX-068
Architecture-Impact: documentation-only
```

Use `implementation` for business changes and `conflict` when a boundary needs resolution. List the actual applicable decision IDs, describe validation and link Owner authorization when required. This declaration is review evidence, not an approval mechanism.

The `Architecture Governance / architecture-policy` workflow checks local metadata and PR acknowledgment. Branch protection and semantic review remain separate; a passing check alone cannot guarantee an agent followed the architecture. New repositories must use the canonical future-app starter and be added to the rollout inventory.
