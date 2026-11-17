import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { buildPreview } from '../build-vercel.mjs';

const good = {
  VERCEL_ENV: 'preview',
  VERCEL_GIT_PROVIDER: 'github',
  VERCEL_GIT_REPO_OWNER: 'redd1975',
  VERCEL_GIT_REPO_SLUG: 'headspace-finance-atlas',
  VERCEL_GIT_PULL_REQUEST_ID: '42',
  VERCEL_GIT_COMMIT_SHA: 'a'.repeat(40)
};
test('Vercel native build uses only synthetic PR data at exact SHA', () => {
  const dir = mkdtempSync(join(tmpdir(), 'hs-preview-'));
  try {
    buildPreview(good, dir);
    const manifest = JSON.parse(readFileSync(join(dir, 'preview-manifest.json'), 'utf8'));
    const data = JSON.parse(readFileSync(join(dir, 'progress.json'), 'utf8'));
    const html = readFileSync(join(dir, 'index.html'), 'utf8');
    assert.equal(manifest.pr_number, 42);
    assert.equal(manifest.commit_sha, 'a'.repeat(40));
    assert.equal(manifest.environment, 'preview');
    assert.equal(data.test_data, 'synthetic');
    assert.equal(data.connected, false);
    assert.ok(html.includes('data-hs-preview="synthetic"'));
  } finally { rmSync(dir, { recursive: true, force: true }); }
});
test('rejects production, unknown repository, and unbound SHA', () => {
  for (const changes of [
    { VERCEL_ENV: 'production' },
    { VERCEL_GIT_REPO_SLUG: 'financial-stewardship' },
    { VERCEL_GIT_PULL_REQUEST_ID: '' },
    { VERCEL_GIT_COMMIT_SHA: 'unverified' },
  ]) assert.throws(() => buildPreview({ ...good, ...changes }, '/tmp/should-not-create-preview'));
});
