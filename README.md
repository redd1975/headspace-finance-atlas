> **Mandatory architecture:** Read [the canonical Xpace / Headspace policy](https://github.com/redd1975/SAAS/blob/70e2d49b131f095cf8fcf01d48e84fff793d614e/architecture/README.md), [AGENTS.md](AGENTS.md) and [.architecture-policy.json](.architecture-policy.json) before changes. Owner-confirmed design is not a production-implementation claim.

# Headspace Finance Execution Tracker

This is a **public-safe, read-only** GitHub Pages dashboard. It does not contain or publish the full internal Finance Execution Atlas or financial records.

## Activate the site (one time)

1. In this repository select **Settings → Pages → Build and deployment → GitHub Actions**.
2. Generate a fine-grained personal access token scoped **only** to private `redd1975/financial-stewardship`, with read-only metadata and Pull requests access.
3. In this public tracker repository, open **Settings → Secrets and variables → Actions → New repository secret**. Set its name to **FINANCE_READ_TOKEN**, and paste the token **only into GitHub**.
4. Go to **Actions → Publish Finance Atlas → Run workflow**.
5. Confirm the deployment succeeds; visit **https://redd1975.github.io/headspace-finance-atlas/**.

If the secret is missing, the site may deploy using the placeholder, labeled **GitHub sync: pending**.

## What runs automatically

- Every 15 minutes, GitHub Actions requests private repo PR state with read-only token access.
- It generates a **sanitized** snapshot including only approved FIN IDs, generic descriptions, agent names and PR state.
- It publishes the website as an artifact using official GitHub Pages actions.
- It never edits the private Finance application, merges PRs, or deploys finance software.
- GitHub Actions does not commit the generated progress back to main; the live deployed website is the refreshed artifact.

## Security and status limits

Public Pages are **not access controlled**. Never publish the original 800 KB internal Atlas or raw private GitHub PR descriptions without a separate redaction review. Do not add secrets to code. This dashboard intentionally displays production deployment as **unknown** rather than inferring deployment from merge. CI and financial safety gates are **not** certified by this public tracker. Keep workflow changes reviewed because Actions may access the private read token.

To add FIN mapping, edit `config/fin-work-packages.json` via a reviewed PR.

## Files

- `site/index.html`: public dashboard
- `site/progress.json`: initial conservative fallback
- `config/fin-work-packages.json`: public allowlist
- `scripts/sync_finance_progress.py`: read-only sync
- `.github/workflows/publish-atlas.yml`: publication workflow
