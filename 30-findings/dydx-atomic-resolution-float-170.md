---
tags:
  - web3/finding
  - status/duplicate
  - web3/bounty
title: 'dYdX v4 atomicResolution Float #170'
updated: '2026-06-05'
---
# dYdX v4 — atomicResolution float64 Off-by-One (#170)

## Summary

| Field | Value |
|-------|-------|
| Report | #170 |
| Protocol | [[40-protocols/dydx-v4]] |
| Status | `status/duplicate` |
| Real bug | **Yes** (IEEE 754 / Log10 precision) |
| Bounty FP | **Partially** — narrow trigger undermines likelihood |

## Finding

In `listing.go`, `atomicResolution` is derived via `math.Log10(float64(...))`, introducing floating-point rounding error and an off-by-one in resolution for certain `referencePrice` values.

## Technical validity

- PoC math is correct — real float precision bug
- Permissionless in theory

## Likelihood problem

Trigger requires `referencePrice` in a narrow band (~10^15–10^16), which is **practically hard** to reach:
- Oracle manipulation at extreme prices, or
- Absurdly priced token listing

## Outcome

Duplicate — likely same float pattern reported before or accepted as known class by dYdX.

## Lessons

1. **Permissionless ≠ Critical** — AI inflates likelihood when impact looks large
2. **Prove parameter space is reachable** before High/Critical
3. Float in Go listing code = known audit finding category — check Solodit first
4. Duplicate can still mean "real but known/narrow"

## AI trap

Labeling "permissionless listing manipulation" as Critical without demonstrating production-reachable `referencePrice` range.

## Preflight for float / Go bugs

- [ ] Bound the trigger range numerically
- [ ] Show realistic path to that state (not just `deal()`)
- [ ] Search dYdX audits + prior reports for Log10/float64
