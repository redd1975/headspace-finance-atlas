#!/usr/bin/env python3
"""Publish an explicitly sanitized read-only status summary from a private GitHub repo."""
import datetime as dt
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "fin-work-packages.json"
OUTPUT = ROOT / "site" / "progress.json"
API = "https://api.github.com"
EXPECTED_REPO = "redd1975/financial-stewardship"
FIN_RE = re.compile(r"(?<![A-Z0-9])FIN[- _]?(\d{2,3})(?!\d)", re.I)

def gh(path, token):
    if not path.startswith("/repos/" + EXPECTED_REPO + "/"):
        raise ValueError("Disallowed GitHub API path")
    request = urllib.request.Request(API + path, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": "Bearer " + token,
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "headspace-public-safe-tracker",
    })
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)

def pages(endpoint, token, max_pages=10):
    items = []
    for page in range(1, max_pages + 1):
        join = "&" if "?" in endpoint else "?"
        batch = gh(endpoint + join + "per_page=100&page=" + str(page), token)
        if not isinstance(batch, list):
            raise ValueError("Expected GitHub array")
        items.extend(batch)
        if len(batch) < 100:
            break
    else:
        raise ValueError("Result exceeded pagination safety limit")
    return items

def ids_in(title):
    return set("FIN" + n.zfill(2) for n in FIN_RE.findall(title or ""))

def status_for(pr):
    if pr.get("merged_at"):
        return "merged — deployment unverified"
    if pr.get("state") == "closed":
        return "closed without merge"
    if pr.get("draft"):
        return "draft PR"
    return "open PR — review pending"

def ci_for(pr, token):
    sha = pr.get("head", {}).get("sha")
    if not sha or not re.fullmatch(r"[0-9a-f]{40}", sha):
        return "unknown"
    runs = gh("/repos/" + EXPECTED_REPO + "/commits/" + sha + "/check-runs?per_page=100", token)
    checks = [c for c in runs.get("check_runs", []) if c.get("name") not in ("", None)]
    if not checks:
        return "not reported"
    # The check-run list can include retries; prefer the latest record per check name.
    latest = {}
    for c in checks:
        name = c["name"]
        if name not in latest or c.get("started_at", "") >= latest[name].get("started_at", ""):
            latest[name] = c
    outcomes = [c.get("conclusion") if c.get("status") == "completed" else None for c in latest.values()]
    if any(x in ("failure", "timed_out", "cancelled", "action_required", "startup_failure") for x in outcomes):
        return "failed"
    if any(x is None for x in outcomes):
        return "running"
    if all(x == "success" for x in outcomes):
        return "passing (reported checks)"
    return "incomplete"

def review_for(pr, token):
    reviews = pages("/repos/" + EXPECTED_REPO + "/pulls/" + str(pr["number"]) + "/reviews", token, max_pages=5)
    author = (pr.get("user") or {}).get("login", "").lower()
    last = {}
    for review in reviews:
        login = (review.get("user") or {}).get("login", "").lower()
        if not login or login == author:
            continue
        if review.get("commit_id") != pr.get("head", {}).get("sha"):
            continue
        if review.get("state") in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED"):
            last[login] = review["state"]
    if any(v == "CHANGES_REQUESTED" for v in last.values()):
        return "changes requested"
    if any(v == "APPROVED" for v in last.values()):
        return "independent GitHub approval recorded"
    return "no independent approval at head"

def deployment_for(pr, token):
    # An exact merged-commit SHA and a successful production environment deployment
    # are necessary; deployment may legitimately remain unknown.
    if not pr.get("merged_at"):
        return "not deployed / unverified"
    sha = pr.get("merge_commit_sha")
    if not sha or not re.fullmatch(r"[a-f0-9]{40}", sha):
        return "unknown"
    path = "/repos/" + EXPECTED_REPO + "/deployments?sha=" + sha + "&per_page=100"
    for deployment in gh(path, token):
        env = (deployment.get("environment") or "").lower()
        if env not in ("production", "prod"):
            continue
        states = gh("/repos/" + EXPECTED_REPO + "/deployments/" + str(deployment["id"]) + "/statuses?per_page=100", token)
        if states and states[0].get("state") == "success":
            return "verified"
    return "unknown"

def main():
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    if cfg.get("source_repo") != EXPECTED_REPO:
        raise ValueError("Unexpected source repository")
    token = os.environ.get("FINANCE_READ_TOKEN", "").strip()
    if not token:
        raise ValueError("FINANCE_READ_TOKEN not configured: refusing to publish stale placeholder as live")
    definitions = {p["id"]: p for p in cfg["packages"]}
    prs = pages("/repos/" + EXPECTED_REPO + "/pulls?state=all&sort=updated&direction=desc", token)
    discovered = {}
    for pr in prs:
        matches = ids_in(pr.get("title", "")) & set(definitions)
        # Explicit curated PR mapping overrides title matching; do not expose private titles.
        for fin, definition in definitions.items():
            if pr["number"] == definition.get("pr_number"):
                matches.add(fin)
        for fin in matches:
            discovered.setdefault(fin, []).append(pr)
    # Collect package IDs from issue titles, but do not interpret issue closure as completion.
    issue_ids = set()
    for issue in pages("/repos/" + EXPECTED_REPO + "/issues?state=all&sort=updated&direction=desc", token):
        if "pull_request" not in issue:
            issue_ids |= ids_in(issue.get("title", ""))
    records = []
    for fin, definition in definitions.items():
        rec = {
            "id": fin, "title": definition["title"], "owner": definition.get("owner"),
            "pr_number": None, "pr_count": len(discovered.get(fin, [])),
            "pr_state": "unknown", "status": definition.get("manual_status") or ("issue recorded" if fin in issue_ids else "not verified"),
            "ci": "unknown", "review": "unknown", "deployment": "unknown", "commit_updated_at": None
        }
        candidates = discovered.get(fin, [])
        if candidates:
            # Prefer open PRs. Otherwise most recently updated PR.
            candidates.sort(key=lambda p: (p.get("state") == "open", p.get("updated_at") or ""), reverse=True)
            chosen = candidates[0]
            # Pulls-list API does not have merged_at or merge_commit_sha: read selected detail.
            pr = gh("/repos/" + EXPECTED_REPO + "/pulls/" + str(chosen["number"]), token)
            rec["pr_number"] = pr["number"]
            rec["pr_state"] = pr.get("state", "unknown")
            rec["status"] = status_for(pr)
            rec["ci"] = ci_for(pr, token)
            rec["review"] = review_for(pr, token)
            rec["deployment"] = deployment_for(pr, token)
            rec["commit_updated_at"] = pr.get("updated_at")
        records.append(rec)
    snap = {
        "connected": True,
        "verified_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "note": "Automatic PR discovery and check/review verification. No private PR text or source data published. GitHub state does not by itself prove financial correctness.",
        "assignments": cfg.get("assignments", []),
        "packages": records,
    }
    OUTPUT.write_text(json.dumps(snap, indent=2) + "\n", encoding="utf-8")
    print("Public-safe sync successful; packages:", len(records), "; mapped PRs:", sum(bool(r["pr_number"]) for r in records))
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print("SYNC FAILED (no fresh snapshot will be published):", type(exc).__name__, str(exc)[:200], file=sys.stderr)
        sys.exit(1)
