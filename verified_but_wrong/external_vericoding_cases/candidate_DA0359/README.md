# External Vericoding Candidate DA0359

Status: **candidate_auto_pack_created_needs_manual_oracle**

Source: `apps`  
Source id: `apps_test_1849`  
Gap category: `trivial_postcondition`  
Confidence: `high`

## NL intent excerpt

```text
Given an integer n, consider all integers from 0 to 10^n - 1, each padded with leading zeros to exactly n digits. A "block" is a maximal consecutive sequence of identical digits. For each length i from 1 to n, count the total number of blocks of length i across all these padded numbers. Output n integers modulo 998244353, where the i-th integer is the number of blocks of length i.
```

## Formal spec excerpt

```dafny
const MOD := 998244353 predicate ValidInput(n: int) { n >= 1 } function BlockCountFormula(n: int, i: int): int requires n >= 1 && 1 <= i <= n { if i == n then 10 else ((2 * 9 * pow(10, n - i - 1, MOD) * 10) + (if i < n - 1 then ((n - 1 - i) * 9 * 9 * pow(10, n - i - 2, MOD) * 10) else 0)) % MOD } predicate ValidResult(result: seq<int>, n: int) requires n >= 1 { |result| == n && (forall k :: 0 <= k < n ==> 0 <= result[k] < MOD) && (n >= 1 ==> result[n-1] == 10) && (forall i :: 0 <= i < n-1 ==> result[i] == BlockCountFormula(n, i+1)) } method solve(n: int) returns (result: seq<int>) requires ValidInput(n) ensures ValidResult(result, n)
```

## Suspected missing requirement

semantic correctness condition

## Bad candidate behavior idea

return 0 or 1 regardless of the input

## Generated files

- `source_record.json`
- `nl_intent.md`
- `formal_spec.dfy`
- `gap_analysis.md`
- `README.md`
- `VALIDATION_STATUS.md`
- `manual_validation.template.json`
- `bad_candidate.py`
- `weak_spec_proxy.py`

## Caveat

This is an adapted demonstration candidate, not a benchmark bug claim, not a real-world vulnerability claim, and not a prevalence estimate.
