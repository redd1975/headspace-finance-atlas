#!/usr/bin/env python3
"""Delete only explicitly tagged preview deployments from an allowlisted Vercel project."""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

PROJECT_ID = "prj_4nRhl8mkbDPCdzKQB171yQvIB80M"
TEAM_ID = "team_HaKGbMxWDpkTL7SNcraQxOLB"
BASE = "https://api.vercel.com"

def request(method: str, path: str, token: str):
    req = urllib.request.Request(BASE + path, method=method,
        headers={"Authorization": "Bearer " + token, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=25) as response:
        raw = response.read()
        return json.loads(raw) if raw else {}

def cleanup(pr: int, token: str) -> int:
    if pr < 1 or not token:
        raise ValueError("A valid PR number and scoped Vercel token are required")
    removed = 0
    until = None
    # Bounded pagination: fail rather than pretending that a partial listing is complete.
    for page in range(20):
        query = {"projectId": PROJECT_ID, "teamId": TEAM_ID, "limit": 100}
        if until is not None:
            query["until"] = until
        result = request("GET", "/v6/deployments?" + urllib.parse.urlencode(query), token)
        if not isinstance(result.get("deployments"), list):
            raise ValueError("Missing Vercel deployments list")
        for d in result["deployments"]:
            meta = d.get("meta") or {}
            if (d.get("projectId") == PROJECT_ID
                    and d.get("target") == "preview"
                    and meta.get("atlasPreviewPr") == str(pr)):
                deployment_id = d.get("uid") or d.get("id")
                if not isinstance(deployment_id, str) or not deployment_id.startswith("dpl_"):
                    raise ValueError("Refused to delete a deployment without an exact Vercel deployment ID")
                request("DELETE", f"/v13/deployments/{deployment_id}?teamId={TEAM_ID}", token)
                removed += 1
        pagination = result.get("pagination") or {}
        next_cursor = pagination.get("next")
        if next_cursor is None:
            return removed
        if until == next_cursor:
            raise ValueError("Stuck Vercel pagination cursor")
        until = next_cursor
    raise ValueError("Exceeded safe Vercel pagination limit")

def main() -> int:
    try:
        pr = int(os.environ["PREVIEW_PR_NUMBER"])
        token = os.environ["ATLAS_PREVIEW_VERCEL_TOKEN"]
        count = cleanup(pr, token)
        print(f"Removed {count} PR-tagged preview deployment(s), no other targets")
        return 0
    except (KeyError, ValueError, OSError, urllib.error.URLError) as exc:
        print(f"PREVIEW CLEANUP FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
