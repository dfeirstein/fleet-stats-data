#!/usr/bin/env python3
r"""Append (or update) today's UTC download snapshot in snapshots.json.

Classification replicates fleet-stats index.html exactly:
  installs = assets matching /\.dmg$/i
  updates  = assets matching /\.tar\.gz$/i or /latest\.json$/i (else-if after installer)
  total    = every asset's download_count
Single page, per_page=100 — same as the dashboard (both undercount past 100 releases,
consistently).
"""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = "dfeirstein/fleet-desktop-releases"
SNAPSHOTS = Path(__file__).resolve().parent.parent / "snapshots.json"

IS_INSTALLER = re.compile(r"\.dmg$", re.I)
IS_UPDATER = re.compile(r"\.tar\.gz$|latest\.json$", re.I)


def fetch_releases():
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/releases?per_page=100",
        headers={"Accept": "application/vnd.github+json"},
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.load(res)


def main():
    releases = fetch_releases()
    total = installs = updates = 0
    per_version = {}
    for r in releases:
        release_total = 0
        for a in r.get("assets") or []:
            n = a["download_count"]
            release_total += n
            if IS_INSTALLER.search(a["name"]):
                installs += n
            elif IS_UPDATER.search(a["name"]):
                updates += n
        total += release_total
        per_version[r["tag_name"]] = release_total

    entry = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "total": total,
        "installs": installs,
        "updates": updates,
        "perVersion": per_version,
    }

    snapshots = json.loads(SNAPSHOTS.read_text()) if SNAPSHOTS.exists() else []
    for i, s in enumerate(snapshots):
        if s["date"] == entry["date"]:
            snapshots[i] = entry
            break
    else:
        snapshots.append(entry)

    SNAPSHOTS.write_text(json.dumps(snapshots, indent=2) + "\n")
    print(f"{entry['date']}: total={total} installs={installs} updates={updates} "
          f"versions={len(per_version)}")


if __name__ == "__main__":
    sys.exit(main())
