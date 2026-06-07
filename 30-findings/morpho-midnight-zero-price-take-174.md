---
tags:
  - web3/finding
  - status/duplicate
  - web3/bounty
title: 'Morpho Midnight Zero-Price take() #174'
updated: '2026-06-05'
---
# Morpho Midnight — Zero-Price take() totalUnits Inflation (#174)

## Summary

| Field | Value |
|-------|-------|
| Report | #174 |
| Protocol | [[40-protocols/morpho-midnight]] |
| Status | `status/duplicate` |
| Real bug | **Probably yes** (cross-lender dilution PoC) |
| FP element | **Partially** — zero-price behavior is tested/documented |

## Finding

At `tick=0`, `take()` inflates `totalUnits` without token transfer (zero-asset settlement). Researcher argued cross-lender dilution via strong PoC.

## Intended behavior evidence

- Test: `testPriceZeroNoSettlementFeeSell` — **expects** zero-settlement behavior
- NatSpec ~L93–94 documents zero-asset settlement semantics
- tick=0 is a **conscious design boundary**, not an accidental miss

## Outcome

Duplicate — likely known or accepted within design limits.

## Lessons

1. **Read test suite before claiming bug** — ground truth beats AI inference
2. "State changes but no token transfer" ≠ automatically a vulnerability
3. Check for `testPriceZero*`, `testZero*`, NatSpec on edge ticks
4. Strong PoC does not override explicit test coverage of behavior

## AI trap

Flagging zero-price accounting as Critical without opening test file that names the exact scenario.

## Preflight grep commands

```bash
rg "testPriceZero|tick.*0|zero.*settlement" --glob '*test*'
rg "totalUnits" path/to/take.sol
```

## Related

- [[40-protocols/morpho-midnight]]
- [[50-reference/ai-bounty-false-positive-playbook]] — step 3 Intended behavior
