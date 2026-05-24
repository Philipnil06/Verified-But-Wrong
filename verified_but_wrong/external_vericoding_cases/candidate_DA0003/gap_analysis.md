# Gap Analysis: DA0003

Status: **candidate only, not validated**.

Source: `apps` / `apps_test_11`
Category: `trivial_postcondition`
Confidence: `high`

## Suspected missing requirement

semantic correctness condition

## Why the formal spec may be weak

formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only

## Candidate bad implementation idea

return 0 or 1 regardless of the input

## NL excerpt

```text
Given n tiles numbered 1 to n, paint tiles according to rules: - Tile can be painted Red if divisible by a (gives p chocolates) - Tile can be painted Blue if divisible by b (gives q chocolates) - If divisible by both a and b, choose the color giving more chocolates Find the maximum total chocolates possible.
```

## Formal spec excerpt

```dafny
predicate ValidInput(n: int, a: int, b: int, p: int, q: int) { n > 0 && a > 0 && b > 0 && p > 0 && q > 0 } function gcd(a: int, b: int): int requires a > 0 && b >= 0 ensures gcd(a, b) > 0 decreases b { if b == 0 then a else gcd(b, a % b) } method solve(n: int, a: int, b: int, p: int, q: int) returns (result: int) requires ValidInput(n, a, b, p, q) ensures result >= 0
```

## Required manual work

A human must inspect the full external task, write a task-specific weak-spec proxy or document the exact proxy, write an intended oracle over selected inputs, and then create manual_validation.json with status validated or rejected.

Caveat: this is an adapted target-validity demonstration candidate, not a benchmark bug claim.