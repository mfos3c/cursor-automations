---
tags:
  - web3/finding
  - status/disputed
  - web3/bounty
title: 'Mezo MUSD Signature Replay Trove #151'
updated: '2026-06-05'
---
# Mezo MUSD — Signature Replay on Trove Reopen (#151)

## Summary

| Field | Value |
|-------|-------|
| Report | #151 |
| Protocol | [[40-protocols/mezo-musd]] |
| Status | `status/disputed` — rejected by program |
| Real bug (researcher view) | Debatable |
| **FP reference (bounty view)** | **Yes** — primary lesson note |

## Researcher claim

`BorrowerOperationsSignatures.nonces` increment only on signature-based paths. When borrower calls `closeTrove()` directly via EOA, nonce is not bumped. Old signature can be replayed against a **new trove** after close→reopen lifecycle.

## Program response (Piotr Dyraga)

1. Recipient is bound in signature — **permit/delegation model**
2. Same security model as **EIP-2612**: long deadline + failure to invalidate = **signer risk**
3. Nonces are sequential — signer can advance when desired
4. Borrower has only one active trove — trove ID omission not material

## Why this is FP from bounty perspective

- Attacker precondition: victim **signed attacker as recipient** (intended third-party delegation)
- Protocol docs encourage delegation
- "Replay" = **unconsumed permit**, industry-standard accepted risk
- AI pattern-matches "nonce not bumped" → SWC-121 / EIP-712 replay → **mislabels design as bug**

## Researcher counter-arguments (for future disputes)

- Direct `closeTrove()` path lacks automatic nonce invalidation unlike permit consume-on-use
- No public `invalidateNonces()` — UX/security gap
- Docs claim "replay protection" but cross-lifecycle gap exists

## **Submit-stop signal**

Before filing signature/nonce bugs on delegation systems:

1. Run **industry analog check** (EIP-2612, Permit2)
2. Ask: did victim sign for attacker as recipient?
3. If yes → likely **disputed**, not Critical

## Related patterns

- EIP-2612 permit signer risk
- SWC-121 only when protocol fails standard replay guarantees **and** no delegation analog applies

## Tags meaning

Use this note in Obsidian preflight when search hits "signature replay", "nonce", "closeTrove", "Mezo", "MUSD".
