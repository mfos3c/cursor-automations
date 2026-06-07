#!/usr/bin/env bash
# Vault → repo: mirror markdown Obsidian wrote (BB-Scan, manual notes) into git for backup/Hermes.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VAULT="${VAULT_PATH:-/Users/mfosec/Documents/Obsidian Vaults/Web3-Security}"

for dir in 20-bounties 30-findings; do
  src="${VAULT}/${dir}"
  dst="${REPO_ROOT}/${dir}"
  if [[ ! -d "$src" ]]; then
    continue
  fi
  mkdir -p "$dst"
  rsync -a --include='*.md' --include='*/' --exclude='*' "$src/" "$dst/"
done

echo "Synced vault → repo: 20-bounties, 30-findings → ${REPO_ROOT}"
