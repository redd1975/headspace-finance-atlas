// Vercel ignoreCommand: exit 0 skips a build, exit 1 allows it.
// This dedicated project must NEVER publish main/production automatically.
const env = process.env;
const isPr = env.VERCEL_ENV === 'preview'
  && env.VERCEL_GIT_PROVIDER === 'github'
  && env.VERCEL_GIT_REPO_OWNER === 'redd1975'
  && env.VERCEL_GIT_REPO_SLUG === 'headspace-finance-atlas'
  && /^[1-9]\d*$/.test(String(env.VERCEL_GIT_PULL_REQUEST_ID ?? ''));
console.log(isPr ? 'Building isolated PR preview' : 'Skipping non-PR or production deployment');
process.exit(isPr ? 1 : 0);
