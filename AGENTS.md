# Headspace Finance Atlas — Development Agent Rules

This repository is the public-safe static Finance Atlas tracker, **not** the private Finance application.

- Follow `docs/UNIVERSAL-PR-PREVIEW-STANDARD.md`, canonical `redd1975/SAAS` policies and per-app safeguards.
- For the Atlas pilot, use **Vercel native Git PR previews**, not GitHub Actions preview deployment. Vercel builds `preview/vercel-build.sh` under `vercel.json`, with synthetic fixture, PR number and exact commit SHA; production builds fail closed.
- Never read or expose private PR descriptions, live finance records, tokens, production databases, live order APIs or secrets in previews.
- Develop on branches, test, open a draft PR, verify an actual Vercel preview URL, then request owner review. Preview Ready requires HTTP smoke and synthetic/commit checks.
- Native Vercel Git integration requires the Owner to authorize GitHub access inside Vercel. Until configured, Vercel API-manual demo URLs are not evidence that automatic PR deployment works.
- GitHub PR-close cleanup and private-app preview authorization are not yet implemented by this pilot; report these gaps instead of claiming Done.
- Do not merge, deploy to existing production apps, bypass reviews, rotate credentials, enable paid resources, or change DNS without explicit Owner approval.
- Developer lifecycle: **Develop → Test → PR → Vercel Git Preview → Verify → Owner Review → Merge → Authorized Production Release**.
