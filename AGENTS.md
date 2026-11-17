# Headspace Finance Atlas — Development Agent Rules

The source site is a **public-safe read-only tracker**, NOT the private Finance application. This repo does not authorize any production change to Finance, People, Till or Skipt.

- Treat `docs/UNIVERSAL-PR-PREVIEW-STANDARD.md` as the default PR-preview protocol for this repository. For architecture-affecting work also consult `redd1975/SAAS` and the relevant app's existing policies; no second architecture register belongs here.
- Every deployable PR must build with only `preview/fixture.json` synthetic data and include the PR number and exact head SHA in `preview-manifest.json`. Never load private GitHub data, live financial records or production credentials into the preview.
- Develop on a feature branch, add tests, open a draft PR, and wait for owner acceptance. Never merge automatically.
- CI preview only: dedicated `headspace-atlas-pr-preview` Vercel project; no production target or GitHub Pages deployment. Workflows must fail for missing token rather than falling back.
- Static Atlas previews may be public; **no other Headspace/Skipt app inherits that public exception**. Protect private app previews with independent auth and isolated test DBs.
- Every preview must pass live HTTP, commit SHA, synthetic fixture and basic mobile checks before Ready is posted. A pushed commit must update the same PR alias. Closed PR resources must be cleaned up without touching other previews.
- Do not weaken checks, trust branch-provided actor/role claims, expose tokens, alter credentials, run paid infrastructure, change production DNS, or release production without explicit owner approval.
- Agent lifecycle: **Develop → Test → Open PR → Preview → Verify → Owner Review → Merge → Authorized Production Release**.
