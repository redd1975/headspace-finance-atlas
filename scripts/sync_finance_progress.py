#!/usr/bin/env python3
"""Read-only, allowlisted GitHub progress -> public-safe snapshot. No private text is copied."""
import datetime as dt
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "fin-work-packages.json"
OUTPUT = ROOT / "site" / "progress.json"
API = "https://api.github.com"

def gh(path, token):
    url = API + path
    request = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": "Bearer " + token,
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "headspace-public-safe-tracker",
    })
    with urllib.request.urlopen(request, timeout=25) as response:
        return json.load(response)

def main():
    cfg = json.loads(CONFIG.read_text())
    token = os.environ.get("FINANCE_READ_TOKEN", "").strip()
    if not token:
        print("FINANCE_READ_TOKEN absent: publishing previously checked-in placeholder unchanged.")
        return 0
    repo = cfg["source_repo"]
    if repo != "redd1975/financial-stewardship":
        raise ValueError("Unexpected source repository")
    records = []
    for entry in cfg["packages"]:
        rec = {
            "id": entry["id"], "title": entry["title"], "owner": entry.get("owner"),
            "pr_number": entry.get("pr_number"), "deployment": "unknown",
            "pr_state": "unknown", "status": entry.get("manual_status") or "unverified",
        }
        number = entry.get("pr_number")
        if number:
            pr = gh(f"/repos/{repo}/pulls/{int(number)}", token)
            rec["pr_state"] = pr.get("state", "unknown")
            if pr.get("merged_at"):
                rec["status"] = "merged (deployment unverified)"
            elif pr.get("state") == "open" and pr.get("draft"):
                rec["status"] = "draft PR"
            elif pr.get("state") == "open":
                rec["status"] = "open PR — review unverified"
            elif pr.get("state") == "closed":
                rec["status"] = "closed without merge"
        records.append(rec)
    snap = {
        "connected": True,
        "verified_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "note": "Read-only PR states verified. CI, reviews and deployment are not attested by this public summary. Refreshes run on GitHub Actions schedule.",
        "assignments": cfg["assignments"],
        "packages": records,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(snap, indent=2) + "\n")
    print("Wrote public-safe snapshot for", len(records), "packages")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (urllib.error.URLError, TimeoutError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print("Synchronization failed; refusing to publish an invented fresh status:", type(exc).__name__, str(exc)[:150], file=sys.stderr)
        sys.exit(1)
