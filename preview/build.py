#!/usr/bin/env python3
"""Build a public-safe, synthetic PR preview for Finance Atlas; never contact production."""
import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "site" / "index.html"

def build(pr: int, sha: str, destination: pathlib.Path) -> None:
    if pr < 1 or not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("PR must be positive and SHA must be 40 lowercase hexadecimal characters")
    markup = SOURCE.read_text(encoding="utf-8")
    if "<body>" not in markup or "</head>" not in markup or "progress.json" not in markup:
        raise ValueError("Atlas HTML does not have the expected static entrypoint")
    banner = (
        '<div data-hs-preview="synthetic" role="status" '
        'style="padding:12px 18px;background:#173d39;color:white;text-align:center;'
        'font:700 13px system-ui">PREVIEW ONLY — synthetic data, no live financial records. '
        f'PR #{pr} · {sha[:12]}</div>'
    )
    markup = markup.replace("<body>", "<body>" + banner, 1)
    fixture = json.loads((ROOT / "preview" / "fixture.json").read_text(encoding="utf-8"))
    if fixture.get("connected") is not False or fixture.get("test_data") != "synthetic":
        raise ValueError("Fixture must explicitly declare disconnected synthetic data")
    if fixture.get("verified_at") is not None:
        raise ValueError("Preview must not imply verified production synchronization")
    manifest = {
        "environment": "preview",
        "pr_number": pr,
        "commit_sha": sha,
        "test_data": "synthetic",
        "owner_acceptance": "pending",
        "known_limitations": ["Static public-safe Atlas only", "No private Finance integration", "No production backend"],
    }
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "index.html").write_text(markup, encoding="utf-8")
    (destination / "progress.json").write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
    (destination / "preview-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--output", default="dist/pr-preview")
    args = parser.parse_args()
    try:
        build(args.pr, args.sha, pathlib.Path(args.output))
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(f"PREVIEW BUILD REFUSED: {error}", file=sys.stderr)
        return 1
    print(f"Built synthetic PR #{args.pr} preview at {args.output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
