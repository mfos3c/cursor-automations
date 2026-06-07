# Web3 Bug Bounty — Cursor Automations

Two-stage pipeline for smart-contract bug bounty discovery and pre-scan. **Automations never submit reports.**

| Automation | Runtime | Schedule (UTC) | TR (~UTC+3) |
|------------|---------|----------------|-------------|
| **BB-Discover** | Cloud Agent | `0 6 * * 1-5` | Weekdays 09:00 |
| **BB-Scan** | Local Agent | `30 6 * * 1-5` | Weekdays 09:30 |

## Architecture (git-only)

```
BB-Discover (cloud)  →  git commit  →  20-bounties/daily-pick-*.md
                                              ↓ git pull
BB-Scan (local)    →  git commit  →  30-findings/*-scan-*.md
                                              ↓ scripts/sync-to-obsidian.sh
Obsidian vault     ←  mirror only (read in Obsidian app)
```

**Git is the source of truth.** Obsidian MCP is not used. Markdown is mirrored into the Web3-Security vault locally for reading.

Prefill: [`automations/bb-discover-prefill.json`](automations/bb-discover-prefill.json), [`automations/bb-scan-prefill.json`](automations/bb-scan-prefill.json)

Prompts: [`automations/bb-discover-prompt.md`](automations/bb-discover-prompt.md), [`automations/bb-scan-prompt.md`](automations/bb-scan-prompt.md)

Config: [`config/vault.yaml`](config/vault.yaml)

---

## Git workflow

### Repo paths (committed)

| Path | Writer | Purpose |
|------|--------|---------|
| `data/snapshot-YYYY-MM-DD.json` | BB-Discover | Normalized program cache |
| `20-bounties/daily-pick-YYYY-MM-DD.md` | BB-Discover | Daily winner + recon prompt |
| `30-findings/{slug}-scan-YYYY-MM-DD.md` | BB-Scan | LEADs, abort signals |
| `30-findings/*.md` (historical) | Imported once | Duplicate radar |

### Local scripts

```bash
# One-time: import existing vault findings into repo
./scripts/sync-from-vault.sh

# Before BB-Scan (09:30 TR): pull cloud output + mirror to Obsidian
./scripts/pull-and-sync.sh

# After BB-Scan commit: mirror new findings into Obsidian
./scripts/sync-to-obsidian.sh
```

Optional cron on your Mac (09:25 TR = 06:25 UTC weekdays):

```cron
25 6 * * 1-5 cd /Users/mfosec/Desktop/cursor_automations && ./scripts/pull-and-sync.sh
```

### Cloud agent PRs

BB-Discover commits to a cloud-agent branch and opens a PR. **Merge to `main`** before BB-Scan runs (or run `./scripts/pull-and-sync.sh` after merge).

---

## Prerequisites

### 1. MCP (minimal)

| MCP | BB-Discover | BB-Scan |
|-----|-------------|---------|
| Bright Data | **Required** | — |
| web3-bbp-rag | — | **Required** (local `~/.cursor/mcp.json`) |

**No obsidian-web3** — all notes via git files.

### 2. Cloud Agent

[Dashboard → Cloud Agents](https://cursor.com/dashboard?tab=cloud-agents) for BB-Discover.

### 3. GitHub

Repo: [github.com/mfos3c/cursor-automations](https://github.com/mfos3c/cursor-automations)

Both automations → **Repository** `mfos3c/cursor-automations` + branch **`main`**.

### 4. Pashov skills (BB-Scan local)

```bash
ls ~/.cursor/skills/pashov/x-ray/SKILL.md
ls ~/.cursor/skills/pashov/solidity-auditor/SKILL.md
```

### 5. Environment variables (BB-Scan)

`ALCHEMY_*_RPC`, `ETHERSCAN_API_KEY`, etc. per [`config/chains.yaml`](config/chains.yaml)

---

## Scoring profile

From [`config/scoring.yaml`](config/scoring.yaml): rep ≤ 90, deposit ≤ $100, reward ≥ $50k, min GO score 60.

---

## Cursor automations (live)

| Automation | ID | Edit |
|------------|-----|------|
| **BB-Discover** | `eca767f4-3c97-4e89-8957-9c2e401b75e7` | [Open](https://cursor.com/automations/eca767f4-3c97-4e89-8957-9c2e401b75e7) |
| **BB-Scan** | `347313ef-4e1c-4fa3-b2eb-7cb704fb2d9f` | [Open](https://cursor.com/automations/347313ef-4e1c-4fa3-b2eb-7cb704fb2d9f) |

### BB-Discover

- Tools: **Bright Data** only
- Outputs: `20-bounties/daily-pick-*.md` + `data/snapshot-*.json` → git commit
- Update editor instructions from [`automations/bb-discover-prompt.md`](automations/bb-discover-prompt.md) after pull

### BB-Scan

- Tools: **web3-bbp-rag** only (local MCP in Cursor Desktop session)
- Step 0: `git pull` → read `20-bounties/daily-pick-*.md`
- Output: `30-findings/*-scan-*.md` → commit → `./scripts/sync-to-obsidian.sh`
- Update editor instructions from [`automations/bb-scan-prompt.md`](automations/bb-scan-prompt.md) after pull

---

## Daily routine

1. **~09:00 TR** — BB-Discover runs (cloud), opens PR
2. **You** — merge PR to `main` (or enable auto-merge)
3. **09:25 TR** — `./scripts/pull-and-sync.sh` (or cron)
4. **~09:30 TR** — BB-Scan runs (local, Desktop open)
5. **After scan** — `./scripts/sync-to-obsidian.sh` if not in prompt
6. **Human** — open Obsidian, review LEADs, manual checklist before PoC

---

## Pilot dry-run

1. Fix Bright Data `API_TOKEN` if 401
2. BB-Discover **Test run** → merge PR → verify `20-bounties/daily-pick-*.md` on `main`
3. `./scripts/pull-and-sync.sh`
4. BB-Scan **Test run** → verify `30-findings/*-scan-*.md` in repo + Obsidian mirror

---

## Safety

- No automatic submission
- Local fork / read-only RPC by default
- Duplicate radar via repo `30-findings/` + web3-bbp-rag

## Related (Obsidian vault — reference only)

Playbooks stay in vault; pipeline I/O is git:

- `50-reference/cursor-automations-bounty-playbook.md`
- `50-reference/pashov-bounty-workflow.md`
- `50-reference/bounty-preflight-checklist.md`
