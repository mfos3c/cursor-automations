#!/usr/bin/env bash
# Morning hook: pull latest discover output from GitHub, mirror into Obsidian vault.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

git pull --rebase origin main
"${REPO_ROOT}/scripts/sync-to-obsidian.sh"

echo "Ready for BB-Scan: check 20-bounties/daily-pick-$(date -u +%Y-%m-%d).md"
