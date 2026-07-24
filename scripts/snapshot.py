#!/usr/bin/env python3
r"""Append (or update) today's UTC download snapshot in snapshots.json.

Classification replicates fleet-stats index.html exactly:
  installs = assets matching /\.dmg$/i          (new installs)
  updates  = assets matching /\.tar\.gz$/i      (update packages delivered)
  checks   = assets matching /latest\.json$/i   (updater heartbeat polls)
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
IS_UPDATE = re.compile(r"\.tar\.gz$", re.I)
IS_CHECK = re.compile(r"latest\.json$", re.I)


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
    total = installs = updates = checks = 0
    per_version = {}
    for r in releases:
        v = {"installs": 0, "updates": 0, "checks": 0}
        for a in r.get("assets") or []:
            n = a["download_count"]
            total += n
            if IS_INSTALLER.search(a["name"]):
                v["installs"] += n
            elif IS_UPDATE.search(a["name"]):
                v["updates"] += n
            elif IS_CHECK.search(a["name"]):
                v["checks"] += n
        installs += v["installs"]
        updates += v["updates"]
        checks += v["checks"]
        per_version[r["tag_name"]] = v

    entry = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "total": total,
        "installs": installs,
        "updates": updates,
        "checks": checks,
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
          f"checks={checks} versions={len(per_version)}")


if __name__ == "__main__":
    sys.exit(main())
