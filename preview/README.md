# Headspace Atlas — Vercel-native PR Preview Pilot

This is a **public-safe, read-only synthetic tracker preview**, NOT the private Finance app.

## Hosting: Vercel directly (no GitHub Actions deployment usage)

- Vercel team: Xpace (`xpace1`)
- Dedicated project: `headspace-atlas-pr-preview` (`prj_4nRhl8mkbDPCdzKQB171yQvIB80M`)
- Git source to connect in Vercel Project Settings: `redd1975/headspace-finance-atlas`
- Integration prerequisites: In Vercel account Git settings, connect GitHub and authorize only the selected repository. At the last inspection, Vercel reported **no GitHub Login Connection**, so automatic PR builds are not yet operational.
- No `ATLAS_PREVIEW_VERCEL_TOKEN` GitHub secret, no Actions-based deployment job, and no production web app or DNS changes.
- Build config: root `vercel.json`; unit tests via `node --test preview/tests/test-vercel.mjs`; build via `node preview/build-vercel.mjs`.
- Vercel-only system variables: `VERCEL_ENV`, `VERCEL_GIT_PROVIDER`, `VERCEL_GIT_REPO_OWNER`, `VERCEL_GIT_REPO_SLUG`, `VERCEL_GIT_PULL_REQUEST_ID`, and `VERCEL_GIT_COMMIT_SHA`. Missing or untrusted values fail closed.
- `ignoreCommand` skips non-PR builds, including production/main. The preview project also has a project-level ignore command so the default branch does not deploy as production.
- `preview/fixture.json` is synthetic, disconnected, and contains no private Finance records; PR/commit markers appear in `preview-manifest.json`.
- Vercel automatically creates per-branch preview links on GitHub PRs when Git integration is active. Verify the exact SHA and deployed HTTP response before marking owner acceptance Ready.
- Vercel's build usage is subject to the team plan. Existing GitHub CI workflows, including the original GitHub Pages production workflow, are separate and may still consume GitHub Actions usage.

## Owner verification

1. Connect GitHub in Vercel's Xpace team; link the dedicated preview project to `redd1975/headspace-finance-atlas`.
2. Check the preview build's production/branch ignore settings before linking.
3. Push a commit to this draft PR. Vercel should build a new synthetic preview and provide its URL on GitHub.
4. Open the URL on iPhone and desktop; check `/preview-manifest.json` for exact PR number + SHA and `/progress.json` for `test_data: synthetic`.
5. Push a second commit and confirm the stable branch preview URL updates.
6. Close a throwaway PR; inspect Vercel's branch/preview retention and manually set a safe retention policy if provider behavior does not delete old deployments.
7. Keep this draft PR unmerged until the owner approves. Production remains unchanged.

## Limits

No private employee, merchant or financial data; no production app access; no real checkout or bank operations. Skipt, Till, People and server-based apps require isolated containers and data, not direct reuse of this public static pilot.
