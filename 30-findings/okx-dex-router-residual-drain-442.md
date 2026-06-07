---
tags:
  - web3/finding
  - status/duplicate
  - web3/bounty
title: 'OKX DEX Router CommissionLib toB Drain #442'
updated: '2026-06-05'
---
# OKX DEX Router — CommissionLib toB Residual Drain (#442)

## Summary

| Field | Value |
|-------|-------|
| Report | #442 |
| Protocol | [[40-protocols/okx-dex-router]] |
| Status | `status/duplicate` |
| Real bug | **Yes** — PoC drains ~200k USDT |
| FP | **No** — duplicate ≠ false positive |

## Finding

`CommissionLib` in **toB mode** sends the router's **full token balance** to the commission recipient instead of the **delta** (commission amount only). Residual ERC20 left on the router from prior swaps can be drained.

## Root cause

Balance-based transfer (`balanceOf(this)`) rather than computed commission delta — same attack surface family as #16 / #444.

## PoC outcome

- PoC passes
- Demonstrates drain of residual balance (~200k USDT in report scenario)
- **No bounty payout** — duplicate / prior art in same program

## Lessons

1. **Duplicate ≠ FP** — technically valid exploit, lost on timing
2. **Same protocol radar** — after #16/#444, any new "router residual" path should trigger duplicate check first
3. **AI trap** — pattern "public + balanceOf(this)" → auto-Critical without program history scan
4. **PoC passing ≠ payout**

## Duplicate context

- Related: [[30-findings/okx-dex-router-invest-refund-444]] (explicit duplicate of #16)
- Same family: residual ERC20 on OKX DEX Router

## Preflight actions for future OKX work

- Search platform for #16, #442, #444 before new router drain reports
- Grep for `balanceOf(address(this))` on outbound transfers
- Check audit known issues for aggregator dust/residual class
