#!/usr/bin/env python3
"""Fail-closed PR preview verification (local or deployed directory)."""
import argparse
import json
import pathlib
import re
import sys

def verify(root: pathlib.Path, pr: int, sha: str) -> None:
    manifest = json.loads((root / "preview-manifest.json").read_text(encoding="utf-8"))
    fixture = json.loads((root / "progress.json").read_text(encoding="utf-8"))
    html = (root / "index.html").read_text(encoding="utf-8")
    if manifest.get("environment") != "preview" or manifest.get("pr_number") != pr or manifest.get("commit_sha") != sha:
        raise ValueError("Preview manifest PR/SHA does not match requested deployment")
    if manifest.get("test_data") != "synthetic" or manifest.get("owner_acceptance") != "pending":
        raise ValueError("Preview must remain synthetic with acceptance pending")
    if fixture.get("test_data") != "synthetic" or fixture.get("connected") is not False or fixture.get("verified_at") is not None:
        raise ValueError("Fixture is not isolated synthetic data")
    if not fixture.get("packages") or not all(str(p.get("id", "")).startswith("SYN") for p in fixture["packages"]):
        raise ValueError("Only synthetic preview identifiers are allowed")
    if 'data-hs-preview="synthetic"' not in html or "viewport" not in html or "progress.json" not in html:
        raise ValueError("Preview banner, mobile viewport, or data link missing")
    bad = re.search(r"ghp_[a-zA-Z0-9]{20}|github_pat_|BEGIN (?:RSA )?PRIVATE KEY|https?://(?:wealth|people|till|order)\.(?:headspacecoffee\.co|skipt\.io)", html, re.I)
    if bad:
        raise ValueError("Potential secret or production app endpoint in static markup")

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=pathlib.Path, required=True)
    p.add_argument("--pr", type=int, required=True)
    p.add_argument("--sha", required=True)
    a = p.parse_args()
    try:
        verify(a.root, a.pr, a.sha)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"PREVIEW VERIFY REFUSED: {exc}", file=sys.stderr)
        return 1
    print("PREVIEW VERIFIED: PR/SHA, synthetic isolation, mobile HTML")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
