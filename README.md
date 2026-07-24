# fleet-stats-data

Daily download snapshots of [dfeirstein/fleet-desktop-releases](https://github.com/dfeirstein/fleet-desktop-releases), appended to `snapshots.json` by a scheduled GitHub Action (06:00 UTC).
Consumed by the dashboard at https://fleet-stats.vercel.app.

Each entry: `{date, total, installs, updates, checks, perVersion: {tag: {installs, updates, checks}}}` —
`installs` = `.dmg` downloads, `updates` = `.tar.gz` update packages delivered, `checks` = `latest.json` updater heartbeat polls.
