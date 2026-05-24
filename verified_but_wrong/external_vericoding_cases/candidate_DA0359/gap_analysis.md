# Gap Analysis: DA0359

Status: **candidate only, not validated**.

Source: `apps` / `apps_test_1849`
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
Given an integer n, consider all integers from 0 to 10^n - 1, each padded with leading zeros to exactly n digits. A "block" is a maximal consecutive sequence of identical digits. For each length i from 1 to n, count the total number of blocks of length i across all these padded numbers. Output n integers modulo 998244353, where the i-th integer is the number of blocks of length i.
```

## Formal spec excerpt

```dafny
const MOD := 998244353 predicate ValidInput(n: int) { n >= 1 } function BlockCountFormula(n: int, i: int): int requires n >= 1 && 1 <= i <= n { if i == n then 10 else ((2 * 9 * pow(10, n - i - 1, MOD) * 10) + (if i < n - 1 then ((n - 1 - i) * 9 * 9 * pow(10, n - i - 2, MOD) * 10) else 0)) % MOD } predicate ValidResult(result: seq<int>, n: int) requires n >= 1 { |result| == n && (forall k :: 0 <= k < n ==> 0 <= result[k] < MOD) && (n >= 1 ==> result[n-1] == 10) && (forall i :: 0 <= i < n-1 ==> result[i] == BlockCountFormula(n, i+1)) } method solve(n: int) returns (result: seq<int>) requires ValidInput(n) ensures ValidResult(result, n)
```

## Required manual work

A human must inspect the full external task, write a task-specific weak-spec proxy or document the exact proxy, write an intended oracle over selected inputs, and then create manual_validation.json with status validated or rejected.

Caveat: this is an adapted target-validity demonstration candidate, not a benchmark bug claim.