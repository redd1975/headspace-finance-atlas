# Pull-request previews — first validated slice

## Scope and safety

This workflow is exclusively for the **public-safe, read-only Finance Atlas**. It is NOT a financial app preview and does not exercise transactions or use the production Finance database. It is a reusable preview-pattern pilot only.

- Trigger: `pull_request` (opened, reopened, synchronize, closed), **same-repository PRs only**; fork PRs receive no deployment credentials or preview.
- Source: PR-head commit, validated synthetic fixture, project-local HTML, static output.
- Deployment: dedicated Vercel project `headspace-atlas-pr-preview` in team `xpace1`, preview target only. No `--prod`, no Git branch integration, no production DNS.
- Preview permalink per PR: `atlas-pr-<N>-headspace-atlas-pr-preview.vercel.app` (requires Vercel to accept alias and a successful smoke test). The URL will remain consistent across PR commits.
- Access: public by design because this Atlas is already public-safe. Never use this pattern as-is for People, Finance, Till, or private data. Those require protected auth previews and isolated backends.
- Data: `preview/fixture.json` is **explicitly synthetic and disconnected**. No tokens or real people, transactions, customers, or API requests. CSP limits connections to self.
- PR comment: an identified bot comment is created/updated *only after* the alias responds with matching PR+SHA manifest and synthetic fixture.
- On close: remove the stable alias and delete eligible preview-target deployments whose metadata matches this PR in the dedicated preview project. No other project or production deployment may be touched.
- No resource charges should be activated without Owner approval.

## One-time configuration (owner/maintainer)

1. Vercel team `xpace1` already contains a *dedicated* project: `headspace-atlas-pr-preview` (ID `prj_4nRhl8mkbDPCdzKQB171yQvIB80M`). Never use `order.skipt.io` or a live site as the target.
2. Create a dedicated, restricted Vercel CI token via Vercel's token UI, scoped to the Xpace team. Limit its lifetime and access as permitted by your Vercel plan. Store it as GitHub Actions repository secret `ATLAS_PREVIEW_VERCEL_TOKEN` in `redd1975/headspace-finance-atlas`. **Never paste the token into a PR, chat, source, logs, or client bundle.**
3. Keep `VERCEL_ORG_ID=team_HaKGbMxWDpkTL7SNcraQxOLB` and `VERCEL_PROJECT_ID=prj_4nRhl8mkbDPCdzKQB171yQvIB80M` as the allowlisted values in the workflow. Changing these requires review.
4. Confirm team policy permits alias `atlas-pr-N-headspace-atlas-pr-preview.vercel.app`. If not, change only the alias template, keeping exact-PR uniqueness.
5. Review and merge the PR that adds this workflow under normal review rules. CI workflows introduced in a PR may not trigger all events until present on the default branch.

No GitHub-Vercel login connection is required **if** the repository secret is present; the workflow uses Vercel CLI with the explicitly pinned project and team.

## Workflow steps

`PR opened or updated → synthetic unit tests → build fixture → security checks → Vercel preview-only deploy → assign stable alias → HTTP/manifest smoke → create/update PR comment.`

`PR closed → remove alias → delete only marked preview deployments (never production) → best-effort closure comment.`

All deployment and clean-up steps fail closed for missing credentials. A preview is never considered Ready without a successful HTTP response and expected manifest.

## Local validation

```bash
python3 -m unittest discover -s preview/tests -v
python3 -m preview.build --pr 42 --sha aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa --output dist/pr-preview
python3 -m preview.verify --root dist/pr-preview --pr 42 --sha aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
```

The real PR workflow should additionally smoke its deployed alias from GitHub Actions.

## Common limitations

- Pilot is public-safe HTML only, with no login, database, external writes, or actual finance interactions.
- GitHub Actions token for Vercel is not provisioned by this source-code PR.
- Publishing static code cannot exercise full Skipt checkout, persistent Node services, People auth, Till integration, or payroll.
- For those apps, use protected PR-specific container + database or a hybrid frontend/backend with sandboxed external adapters.
- Deployment pruning is restricted to the dedicated project, metadata, and Preview target; Vercel may retain provider-owned build logs.
