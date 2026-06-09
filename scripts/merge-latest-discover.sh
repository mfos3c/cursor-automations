#!/usr/bin/env bash
# Fallback bridge: copy newest daily-pick from a cursor/*discovery* branch → main.
# Primary path is .github/workflows/discover-bridge.yml on cloud push.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

git fetch origin main 2>/dev/null || git fetch origin

best_branch=""
best_date=""
best_file=""

while IFS= read -r ref; do
  branch="${ref// /}"
  branch="${branch#origin/}"
  while IFS= read -r pick; do
    [[ -z "$pick" ]] && continue
    date="${pick#20-bounties/daily-pick-}"
    date="${date%.md}"
    if [[ -z "$best_date" || "$date" > "$best_date" ]]; then
      best_date="$date"
      best_branch="$branch"
      best_file="$pick"
    fi
  done < <(git ls-tree -r --name-only "origin/$branch" 20-bounties/ 2>/dev/null | grep -E 'daily-pick-[0-9]{4}-[0-9]{2}-[0-9]{2}\.md$' || true)
done < <(git branch -r | grep -E 'origin/cursor/.*(discovery|bug-bounty-program)' | grep -v HEAD || true)

if [[ -z "$best_file" ]]; then
  echo "merge-latest-discover: no daily-pick on remote discover branches"
  exit 0
fi

if git cat-file -e "origin/main:$best_file" 2>/dev/null; then
  echo "merge-latest-discover: main already has $best_file"
  exit 0
fi

if [[ -f "$REPO_ROOT/$best_file" ]]; then
  echo "merge-latest-discover: working tree already has $best_file (unpushed?)"
  exit 0
fi

echo "merge-latest-discover: bridging $best_file from origin/$best_branch"
git checkout "origin/$best_branch" -- "$best_file"
git add "$best_file"
git commit -m "chore: bridge $best_file from $best_branch [merge-latest-discover]"

if git push origin main; then
  echo "merge-latest-discover: pushed to main"
else
  echo "merge-latest-discover: push failed (remote may be ahead — pull will reconcile)" >&2
  exit 0
fi
