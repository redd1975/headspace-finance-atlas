// Vercel-native PR preview generator. No GitHub Actions, external APIs, or live data.
// Fail closed for non-PR builds and other Git providers/repositories.
import { readFileSync, mkdirSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';

export function buildPreview(env, outDir = 'dist/pr-preview') {
  const prRaw = String(env.VERCEL_GIT_PULL_REQUEST_ID ?? '');
  const sha = String(env.VERCEL_GIT_COMMIT_SHA ?? '');
  const pr = Number(prRaw);
  if (env.VERCEL_ENV !== 'preview'
      || env.VERCEL_GIT_PROVIDER !== 'github'
      || env.VERCEL_GIT_REPO_OWNER !== 'redd1975'
      || env.VERCEL_GIT_REPO_SLUG !== 'headspace-finance-atlas'
      || !/^[1-9]\d*$/.test(prRaw) || !Number.isSafeInteger(pr)
      || !/^[0-9a-f]{40}$/.test(sha)) {
    throw Error('Refused: exact GitHub PR, SHA, repo, and preview environment required');
  }

  const base = resolve('.');
  const originalHtml = readFileSync(join(base, 'site/index.html'), 'utf8');
  const fixture = JSON.parse(readFileSync(join(base, 'preview/fixture.json'), 'utf8'));
  if (!originalHtml.includes('<body>') || !originalHtml.includes('</head>')
      || !originalHtml.includes('progress.json')) {
    throw Error('Unexpected source HTML; refusing to publish');
  }
  if (fixture.test_data !== 'synthetic' || fixture.connected !== false
      || fixture.verified_at !== null || !Array.isArray(fixture.packages)
      || !fixture.packages.length || !fixture.packages.every(x => /^SYN/.test(x.id ?? ''))) {
    throw Error('Refused: fixture is not explicitly isolated synthetic data');
  }
  if (/https?:\/\/(?:wealth|people|till|order)\.(?:headspacecoffee\.co|skipt\.io)/i.test(originalHtml)) {
    throw Error('Refused: production application endpoint in preview HTML');
  }

  const banner = '<div data-hs-preview="synthetic" role="status" '
    + 'style="padding:12px 18px;background:#173d39;color:white;text-align:center;font:700 13px system-ui">'
    + 'PREVIEW ONLY — synthetic data, no live financial records. PR #' + pr
    + ' · ' + sha.slice(0, 12) + '</div>';
  const html = originalHtml.replace('<body>', '<body>' + banner);
  const manifest = {
    environment: 'preview', pr_number: pr, commit_sha: sha,
    test_data: 'synthetic', owner_acceptance: 'pending',
    known_limitations: ['Static public-safe tracker only', 'No real Finance API or records']
  };

  const target = resolve(outDir);
  mkdirSync(target, { recursive: true });
  writeFileSync(join(target, 'index.html'), html);
  writeFileSync(join(target, 'progress.json'), JSON.stringify(fixture, null, 2) + '\n');
  writeFileSync(join(target, 'preview-manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
  // Local build verification: Vercel will only mark the deployment ready after this command succeeds.
  if (JSON.parse(readFileSync(join(target, 'preview-manifest.json'), 'utf8')).commit_sha !== sha) {
    throw Error('Preview SHA verification failed');
  }
  return { pr, sha, outDir: target };
}

if (process.argv[1] && resolve(process.argv[1]) === new URL(import.meta.url).pathname) {
  try {
    const result = buildPreview(process.env);
    process.stdout.write('Synthetic Vercel PR preview built: #' + result.pr + ' ' + result.sha + '\n');
  } catch (err) {
    console.error('PREVIEW BUILD REFUSED:', err.message);
    process.exitCode = 1;
  }
}
