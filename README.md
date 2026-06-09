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

## Re-import RAG corpus (421 docs from web3-rag-mcp)

When `/Users/mfosec/web3-rag-mcp/content/` updates:

```bash
python3 scripts/import-rag-corpus.py
```

Vault: open **`Web3 Security`** → start at **`00-index/Web3 Graph Hub`**.

Obsidian Importer plugin enabled for other formats: [help](https://obsidian.md/help/plugins/importer).

---

## Auto bridge (cloud → main → Obsidian)

Cloud agents push to `cursor/*` branches **without opening PRs**. Two layers fix that:

| Layer | What | When |
|-------|------|------|
| **GitHub Actions** | `discover-bridge.yml` / `scan-bridge.yml` copy picks & findings → `main` | On cloud branch push |
| **Mac launchd** | `pull-and-sync.sh` → Obsidian vault | Mon–Fri **09:25** local time |

Install Mac sync (once):

```bash
./scripts/install-macos-sync.sh
```

Log: `~/Library/Logs/cursor-automations-pull-sync.log`

Manual test anytime:

```bash
./scripts/pull-and-sync.sh
```

Fallback if Actions lag: `scripts/merge-latest-discover.sh` (called from pull-and-sync).

---

## Sync scripts

```bash
./scripts/pull-and-sync.sh          # fetch + merge discover + pull main + vault sync
./scripts/merge-latest-discover.sh  # cloud branch → main (fallback)
./scripts/sync-to-obsidian.sh       # repo → vault only
./scripts/sync-from-obsidian.sh     # vault → repo backup
./scripts/sync-from-vault.sh        # one-time historical import
```

---

## Daily routine (hands-off)

1. **09:00** — BB-Discover cron (cloud) → branch push → **GitHub Action → main**
2. **09:25** — launchd `pull-and-sync` → **Obsidian vault**
3. **09:30** — BB-Scan local (Desktop open, obsidian-web3 + web3-bbp-rag)
4. Optional `./scripts/sync-from-obsidian.sh` → git backup

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
