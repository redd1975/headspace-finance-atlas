#!/usr/bin/env bash
# Vercel Git Integration builds PR previews without GitHub Actions.
set -euo pipefail

if [[ "${VERCEL_ENV:-}" != "preview" ]]; then
  echo "REFUSED: this project is preview-only; production deployments are disabled by build guard" >&2
  exit 1
fi
if [[ ! "${VERCEL_GIT_PULL_REQUEST_ID:-}" =~ ^[1-9][0-9]*$ ]]; then
  echo "REFUSED: missing Git PR number; only actual pull-request builds are allowed" >&2
  exit 1
fi
if [[ ! "${VERCEL_GIT_COMMIT_SHA:-}" =~ ^[a-f0-9]{40}$ ]]; then
  echo "REFUSED: missing exact Git commit SHA" >&2
  exit 1
fi

python3 -m unittest discover -s preview/tests -v
python3 -m preview.build --pr "$VERCEL_GIT_PULL_REQUEST_ID" --sha "$VERCEL_GIT_COMMIT_SHA" --output dist/pr-preview
python3 -m preview.verify --root dist/pr-preview --pr "$VERCEL_GIT_PULL_REQUEST_ID" --sha "$VERCEL_GIT_COMMIT_SHA"
echo "Synthetic, PR-specific Vercel build complete. Deployment readiness still requires HTTP smoke."
