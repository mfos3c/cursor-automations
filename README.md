# Web3 Bug Bounty — Cursor Automations

Two-stage pipeline for smart-contract bug bounty discovery and pre-scan. **Automations never submit reports.**

| Automation | Runtime | Schedule (UTC) | TR (~UTC+3) |
|------------|---------|----------------|-------------|
| **BB-Discover** | Cloud Agent | `0 6 * * 1-5` | Weekdays 09:00 |
| **BB-Scan** | Local Agent | `30 6 * * 1-5` | Weekdays 09:30 |

## Architecture

```
BB-Discover (cloud)  →  20-bounties/daily-pick-*.md  →  BB-Scan (local)  →  30-findings/*-scan-*.md
```

Prefill definitions: [`automations/bb-discover-prefill.json`](automations/bb-discover-prefill.json), [`automations/bb-scan-prefill.json`](automations/bb-scan-prefill.json)

Full prompts: [`automations/bb-discover-prompt.md`](automations/bb-discover-prompt.md), [`automations/bb-scan-prompt.md`](automations/bb-scan-prompt.md)

---

## Prerequisites

### 1. MCP Dashboard ([cursor.com → MCP](https://cursor.com/settings/mcp))

Automations only resolve **dashboard-connected** MCP servers.

| MCP | BB-Discover | BB-Scan | Action |
|-----|-------------|---------|--------|
| Bright Data | Required | — | Verify plugin connected |
| obsidian-web3 | Optional fallback | **Required** | Add + connect |
| web3-bbp-rag | — | **Required** | Add + connect |
| web3-rag | — | Optional | Recommended |

Local-only MCPs (`cursor-ide-browser`, project `mcp.json`) **do not work** in Automations.

If the editor shows **Set up MCP** on a row, fix connection before saving.

### 2. Cloud Agent

Enable at [cursor.com/dashboard → Cloud Agents](https://cursor.com/dashboard?tab=cloud-agents) for BB-Discover.

### 3. GitHub repo (BB-Discover cloud)

Cloud agents need this repo on GitHub:

1. Create remote repo (e.g. `your-user/cursor-automations`)
2. Push this folder
3. In BB-Discover automation editor → set **Repository** to that repo + `main`

BB-Scan prefill uses `gitConfig.repo: mfosec/cursor_automations` — **update to your GitHub path** in the editor.

### 4. Pashov skills (BB-Scan local)

```bash
ls ~/.cursor/skills/pashov/x-ray/SKILL.md
ls ~/.cursor/skills/pashov/solidity-auditor/SKILL.md
# Update: cd ~/.cursor/skills/pashov && git pull
```

### 5. Optional config images

Add reference images to extend chain/service maps:

- `config/chains.jpeg` → extend [`config/chains.yaml`](config/chains.yaml)
- `config/services_activate.jpg` → extend [`config/services.yaml`](config/services.yaml)

### 6. Environment variables (BB-Scan)

Set in shell or `.env` (not committed):

- `ALCHEMY_*_RPC` / `INFURA_*_RPC` per chain in `config/chains.yaml`
- `ETHERSCAN_API_KEY`, `ARBISCAN_API_KEY`, etc.

---

## Scoring profile

From [`config/scoring.yaml`](config/scoring.yaml):

- HackenProof reputation: **90** (skip if program requires higher)
- Max deposit: **$100** (skip if higher)
- Min reward: **$50,000**
- Min score for GO: **60**
- Prefer new/updated within **14 days**

---

## HackenProof (login-gated)

The HackenProof dashboard requires an authenticated session. Cloud BB-Discover may mark HackenProof programs as `confidence: low` without your cookies.

**Workarounds:**

1. **Weekly local sync** — export program list to `data/hackenproof-manual-YYYY-MM-DD.json` (same schema as snapshot)
2. **Browser session** — not supported in cloud Automations; use manual sync
3. **Pilot without HackenProof** — Immunefi + Sherlock + Cantina first

Reputation filter still applies when data is available: skip programs requiring rep > 90.

---

## Create automations in Cursor

**BB-Discover** was opened in the Automations editor with prefill from `automations/bb-discover-prefill.json`.

**BB-Scan** — if the second editor tab did not open, create manually from [`automations/bb-scan-prefill.json`](automations/bb-scan-prefill.json).

### BB-Discover (editor checklist)

- Name: `Web3 BB Program Discovery`
- Trigger: Cron `0 6 * * 1-5`
- Runtime: **Cloud**
- Tools: MCP → Bright Data
- Instructions: [`automations/bb-discover-prompt.md`](automations/bb-discover-prompt.md)
- Repository: `mfos3c/cursor-automations` on GitHub — https://github.com/mfos3c/cursor-automations

**Important:** Cursor dashboard GitHub is connected as `turnikesistemleri`. To use this repo in cloud automations, click **Add Repositories** in the automation editor and grant Cursor access to `mfos3c/cursor-automations` (GitHub login as `mfos3c` may be required).

### BB-Scan (editor checklist)

- Name: `Web3 BB Pre-Scan Pipeline`
- Trigger: Cron `30 6 * * 1-5`
- Runtime: **Local**
- Tools: MCP → obsidian-web3, web3-bbp-rag
- Instructions: [`automations/bb-scan-prompt.md`](automations/bb-scan-prompt.md)
- Repository: optional (local path `/Users/mfosec/Desktop/cursor_automations` works)

---

## Pilot dry-run

### Step 1 — MCP check

- [ ] obsidian-web3 connected in dashboard
- [ ] web3-bbp-rag connected
- [ ] Bright Data connected

### Step 2 — BB-Discover manual run

1. Automations → BB-Discover → **Run once**
2. Expect: `data/snapshot-YYYY-MM-DD.json` in repo (after cloud push) or run locally once
3. Expect: Obsidian `20-bounties/daily-pick-YYYY-MM-DD.md` with verdict, score, recon_prompt
4. Verify: no repo clone, no PoC, no submit

### Step 3 — BB-Scan manual run

1. Confirm daily pick has `verdict: GO`
2. Run BB-Scan once (local)
3. Expect: `30-findings/{slug}-scan-YYYY-MM-DD.md` with LEADs
4. Verify: x-ray + auditor ran on in-scope paths only

### Step 4 — Abort test

Re-run BB-Scan against a target with known duplicate pattern (e.g. OKX router family in your vault). Expect `ABORT_DUPLICATE_RISK` and no clone.

### Step 5 — Human handoff

When scan returns LEADs:

1. Open Agent chat
2. `@20-bounties/daily-pick-*.md` + `@30-findings/*-scan-*.md`
3. Manual checklist sections 3–7 before PoC
4. Submit only after human GO

---

## Outputs

| Path | Writer | Content |
|------|--------|---------|
| `data/snapshot-YYYY-MM-DD.json` | BB-Discover | All normalized programs |
| `data/daily-pick-YYYY-MM-DD.md` | BB-Discover fallback | If Obsidian MCP unavailable on cloud |
| `20-bounties/daily-pick-YYYY-MM-DD.md` | BB-Discover | Daily winner + recon prompt |
| `30-findings/{slug}-scan-YYYY-MM-DD.md` | BB-Scan | LEADs, abort signals |

---

## Safety

- No automatic submission to any platform
- Respect program prohibited_actions and Immunefi exclusions
- Local fork / read-only RPC by default
- Known issues and prior audits = duplicate risk — abort first

## Related (Obsidian)

- `50-reference/cursor-automations-bounty-playbook.md`
- `50-reference/pashov-bounty-workflow.md`
- `50-reference/bounty-preflight-checklist.md`
