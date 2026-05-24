# External Vericoding Candidate DA0258

Status: **candidate_auto_pack_created_needs_manual_oracle**

Source: `apps`  
Source id: `apps_test_1212`  
Gap category: `trivial_postcondition`  
Confidence: `high`

## NL intent excerpt

```text
Given a fence with n planks of heights, find k consecutive planks with the minimum sum of heights. Return the 1-indexed starting position of such a sequence. If multiple solutions exist, return any valid one.
```

## Formal spec excerpt

```dafny
function sum_window(heights: seq<int>, start: int, k: int): int requires 0 <= start requires start + k <= |heights| requires k > 0 decreases k { if k == 1 then heights[start] else heights[start] + sum_window(heights, start + 1, k - 1) } predicate ValidInput(n: int, k: int, heights: seq<int>) { 1 <= k <= n && |heights| == n && forall i :: 0 <= i < n ==> 1 <= heights[i] <= 100 } predicate ValidResult(result: int, n: int, k: int, heights: seq<int>) requires ValidInput(n, k, heights) { 1 <= result <= n-k+1 && forall start :: 0 <= start <= n-k ==> sum_window(heights, result-1, k) <= sum_window(heights, start, k) && forall start :: 0 <= start < result-1 ==> sum_window(heights, start, k) > sum_window(heights, result-1, k) } method solve(n: int, k: int, heights: seq<int>) returns (result: int) requires ValidInput(n, k, heights) ensures ValidResult(result, n, k, heights)
```

## Suspected missing requirement

semantic correctness condition

## Bad candidate behavior idea

return a range/shape-valid but semantically wrong value

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
