#!/usr/bin/env bash
# Morning hook (09:25 TR): merge discover branch if needed, pull main, mirror → Obsidian.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

git fetch origin

# Fallback if GitHub Action did not run yet
"${REPO_ROOT}/scripts/merge-latest-discover.sh" || true

git pull --rebase origin main
"${REPO_ROOT}/scripts/sync-to-obsidian.sh"

echo "Ready for BB-Scan: check 20-bounties/daily-pick-$(date -u +%Y-%m-%d).md"
