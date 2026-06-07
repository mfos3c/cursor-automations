#!/usr/bin/env bash
# One-time / occasional import: vault historical findings → repo (for git-backed duplicate radar).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VAULT="${VAULT_PATH:-/Users/mfosec/Documents/Obsidian Vaults/Web3-Security}"

mkdir -p "${REPO_ROOT}/30-findings"
if [[ -d "${VAULT}/30-findings" ]]; then
  rsync -a --include='*.md' --include='*/' --exclude='*' "${VAULT}/30-findings/" "${REPO_ROOT}/30-findings/"
  echo "Imported vault 30-findings → ${REPO_ROOT}/30-findings"
else
  echo "No vault 30-findings at ${VAULT}" >&2
  exit 1
fi
