#!/usr/bin/env bash
# Install launchd job: weekdays 09:25 TR → pull main + sync Obsidian vault.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLIST_SRC="${REPO_ROOT}/scripts/com.cursor-automations.pull-sync.plist"
PLIST_DST="${HOME}/Library/LaunchAgents/com.cursor-automations.pull-sync.plist"
LOG="${HOME}/Library/Logs/cursor-automations-pull-sync.log"

mkdir -p "${HOME}/Library/LaunchAgents"
mkdir -p "${HOME}/Library/Logs"
touch "$LOG"

cp "$PLIST_SRC" "$PLIST_DST"
launchctl bootout "gui/$(id -u)/com.cursor-automations.pull-sync" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_DST"

echo "Installed: $PLIST_DST"
echo "Schedule: Mon–Fri 09:25 (local time)"
echo "Log: $LOG"
echo "Test now: ${REPO_ROOT}/scripts/pull-and-sync.sh"
