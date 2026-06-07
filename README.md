# Web3 Bug Bounty — Cursor Automations

Two-stage pipeline. **Obsidian Web3-Security vault is the system memory.** Automations never submit reports.

| Automation | Runtime | Schedule (UTC) | TR |
|------------|---------|----------------|-----|
| **BB-Discover** | Cloud | `0 6 * * 1-5` | 09:00 |
| **BB-Scan** | Local | `30 6 * * 1-5` | 09:30 |

## Architecture (Obsidian-first)

```
                    ┌─────────────────────────────┐
                    │  Obsidian Web3-Security     │  ← CANONICAL (graph, wikilinks)
                    │  20-bounties/ 30-findings/  │
                    └────────────▲──────────▲─────┘
                                 │          │
              sync-to-obsidian   │          │  obsidian-web3 MCP
              (after PR merge)   │          │  (BB-Scan read/write)
                                 │          │
┌──────────────┐    git PR   ┌───┴──────────┴───┐    web3-bbp-rag
│ BB-Discover  │ ─────────► │ cursor-automations│ ◄── BB-Scan local
│   (cloud)    │            │  (transport only) │
└──────────────┘            └───────────────────┘
                                      ▲
                              Hermes / future agents
```

| Layer | Role |
|-------|------|
| **Obsidian** | Canonical notes, graph, duplicate radar, human + Hermes |
| **web3-bbp-rag** | Semantic prior-art search (complements vault) |
| **Git repo** | Cloud agent bridge; backup after `sync-from-obsidian.sh` |

Playbook: Obsidian `50-reference/cursor-automations-bounty-playbook.md`

---

## MCP

| MCP | BB-Discover | BB-Scan |
|-----|-------------|---------|
| Bright Data | Required | — |
| **obsidian-web3** | — (cloud can't) | **Required** |
| **web3-bbp-rag** | — | **Required** |

BB-Scan Tools: **obsidian-web3 + web3-bbp-rag** (not git-only).

---

## Sync scripts

```bash
# After cloud PR merged → vault (before BB-Scan)
./scripts/pull-and-sync.sh

# Vault → git backup (after BB-Scan writes to Obsidian)
./scripts/sync-from-obsidian.sh

# One-time: import historical vault findings into repo mirror
./scripts/sync-from-vault.sh
```

Cron (09:25 TR): `25 6 * * 1-5 cd .../cursor_automations && ./scripts/pull-and-sync.sh`

---

## Daily routine

1. BB-Discover cloud run → PR
2. Merge PR → `./scripts/pull-and-sync.sh`
3. BB-Scan local (Desktop open, obsidian-web3 connected)
4. Optional `./scripts/sync-from-obsidian.sh` → git backup
5. Obsidian graph + Hermes read vault

---

## Live automations

| Name | ID |
|------|-----|
| BB-Discover | `eca767f4-3c97-4e89-8957-9c2e401b75e7` |
| BB-Scan | `347313ef-4e1c-4fa3-b2eb-7cb704fb2d9f` |

Update BB-Scan editor: restore **obsidian-web3** MCP + instructions from `automations/bb-scan-prompt.md`.

Prompts: [`automations/bb-discover-prompt.md`](automations/bb-discover-prompt.md), [`automations/bb-scan-prompt.md`](automations/bb-scan-prompt.md)

Config: [`config/vault.yaml`](config/vault.yaml)

---

## Why git exists at all

Cloud agents **cannot** reach local Obsidian MCP. Git is not the memory layer — it is the **inbound pipe** for BB-Discover. Everything that matters lives in the vault for graph, Hermes, and you.
