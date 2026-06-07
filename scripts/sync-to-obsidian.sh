#!/usr/bin/env bash
# Copy pipeline markdown from git repo → Obsidian vault (local read-only mirror).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VAULT="${VAULT_PATH:-/Users/mfosec/Documents/Obsidian Vaults/Web3-Security}"

for dir in 20-bounties 30-findings; do
  src="${REPO_ROOT}/${dir}"
  dst="${VAULT}/${dir}"
  if [[ ! -d "$src" ]]; then
    continue
  fi
  mkdir -p "$dst"
  rsync -a --include='*.md' --include='*/' --exclude='*' "$src/" "$dst/"
done

echo "Synced repo → vault: 20-bounties, 30-findings → ${VAULT}"
