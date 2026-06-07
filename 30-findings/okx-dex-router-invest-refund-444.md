---
tags:
  - web3/finding
  - status/duplicate
  - web3/bounty
title: 'OKX DEX Router smartSwapByInvestWithRefund #444'
updated: '2026-06-05'
---
# OKX DEX Router — smartSwapByInvestWithRefund Drain (#444)

## Summary

| Field | Value |
|-------|-------|
| Report | #444 |
| Protocol | [[40-protocols/okx-dex-router]] |
| Status | `status/duplicate` of **#16** |
| Real bug | **Yes** |
| FP | **No** |

## Finding

`smartSwapByInvestWithRefund` is public and uses `balanceOf(this)` (or equivalent full-balance logic) to transfer tokens, allowing anyone to drain residual ERC20 balance accumulated on the router.

## Root cause

Same residual-drain class as report #16 — different entry function, identical economic attack.

## Outcome

Marked **duplicate of #16** by program. No separate payout.

## Lessons

1. **Do not file second endpoint without duplicate radar** — #444 was doomed once #16 existed
2. **Same contract, different function** = duplicate if root cause is shared balance-drain pattern
3. **AI trap** — seeing new public swap function + balance drain and treating as novel Critical
4. Before PoC: search closed reports for "residual", "dust", "balanceOf(this)" on same router

## Related

- [[30-findings/okx-dex-router-residual-drain-442]] — same family, CommissionLib path
- [[40-protocols/okx-dex-router]] — MOC for all OKX router findings

## Submit-stop rule

If Obsidian or platform shows #16 or #444 class on OKX DEX Router → **do not submit** another residual drain variant without novel root cause.
