# Atlas preview — Vercel-native, no GitHub Actions minutes

This is a **public-safe synthetic static preview** for the Finance Atlas tracker, NOT the private Finance app. It uses a dedicated Vercel project `headspace-atlas-pr-preview` (Xpace team); it never touches the GitHub Pages main-branch publishing flow, the private Finance database, or real customers.

## Preferred workflow

`Claude pushes branch → GitHub PR → Vercel Git Integration automatically deploys PR SHA → Vercel Git status/link in PR → owner tests → new commit updates PR preview.`

No new GitHub Actions workflow is introduced by this PR. Instead, `vercel.json` invokes `preview/vercel-build.sh` inside Vercel builds. The build fails unless `VERCEL_ENV=preview`, a real `VERCEL_GIT_PULL_REQUEST_ID` exists, and `VERCEL_GIT_COMMIT_SHA` is a 40-character hash. Unit tests, synthetic build, and exact-SHA/fixture verification run inside Vercel. No production release path exists in this script.

Only `preview/fixture.json` is served. The data is fictional, disconnected, and marked Preview. All live finance APIs, private PR data, emails, payments and background workers are absent.

## One-time owner action — Vercel Git connection

The Vercel account has **no GitHub Login Connection**. Connecting the Vercel account inside ChatGPT does not connect GitHub to Vercel.

1. In Vercel, open Account Settings → Git, select **Connect GitHub** and authorize the appropriate repositories, including `redd1975/headspace-finance-atlas`. Confirm the Xpace team can import it.
2. In Xpace → Project `headspace-atlas-pr-preview`, link/import the same GitHub repository. If this unlinked project cannot be connected in the UI, create a new **dedicated preview-only Vercel project** with the same config; do not change any production project.
3. Configure the project Framework Preset to **Other**, Build Command `bash preview/vercel-build.sh`, Output Directory `dist/pr-preview` (repo-root working directory). These settings are also in `vercel.json`.
4. Enable Vercel's GitHub PR checks/comments and protect access for non-public-safe apps. For this Atlas pilot the content is synthetic/public-safe; never apply the public-access exception to People, Till, Finance, Ordering or Membership.
5. Ensure PR builds show `VERCEL_GIT_PULL_REQUEST_ID` and `VERCEL_GIT_COMMIT_SHA`; if not, **do not fabricate them**, diagnose the Git integration.
6. Open/update this pilot PR. The Vercel Git connection—not GitHub Actions—must build and post its own preview URL.

No GitHub repository secret `ATLAS_PREVIEW_VERCEL_TOKEN` is needed for the native Git workflow. Do not create or share a new token solely for this workflow.

## Already verified vs. still pending

- **Verified:** A separate synthetic deployment was manually uploaded directly through the Vercel API, and its three HTTP routes (`/`, `/progress.json`, `/preview-manifest.json`) returned 200 with correct PR #2 and exact SHA. This proves the static content is hostable without GitHub Actions.
- **Pending:** Automatic GitHub PR-triggered build (blocked on Vercel GitHub Login Connection), automatic same-PR update via Git, and PR-close cleanup.
- `preview/cleanup.py` is an **optional allowlisted cleanup script**, not wired automatically while Git connection/close events are unavailable. Vercel deployment retention and PR-close cleanup must be evaluated before claiming universal preview completion.
- This pilot cannot exercise backend/order/payroll/financial workflows and must not be represented as the real Finance application.

## Local test commands

```bash
python3 -m unittest discover -s preview/tests -v
python3 -m preview.build --pr 42 --sha aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa --output dist/pr-preview
python3 -m preview.verify --root dist/pr-preview --pr 42 --sha aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
```

Vercel hosting/bandwidth/build usage may count toward plan limits. Vercel Git-based builds do **not** consume GitHub Actions minutes.
