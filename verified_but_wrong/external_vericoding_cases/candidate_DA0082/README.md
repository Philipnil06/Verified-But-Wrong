# External Vericoding Candidate DA0082

Status: **candidate_auto_pack_created_needs_manual_oracle**

Source: `apps`  
Source id: `apps_test_448`  
Gap category: `trivial_postcondition`  
Confidence: `high`

## NL intent excerpt

```text
Given n children numbered 1 to n, where child i needs at least a_i candies. Children initially line up in order 1, 2, ..., n. Distribution algorithm: 1. Give m candies to the first child in line 2. If the child has received enough candies (≥ a_i), they go home 3. Otherwise, the child goes to the end of the line 4. Repeat until all children go home Find which child goes home last.
```

## Formal spec excerpt

```dafny
predicate ValidInput(n: int, m: int, a: seq<int>) { n > 0 && m > 0 && |a| == n && forall i :: 0 <= i < |a| ==> a[i] > 0 } predicate ValidResult(result: int, n: int) { 1 <= result <= n } function SumCandiesStillNeeded(queue: seq<seq<int>>): nat requires forall child :: child in queue ==> |child| == 3 && child[0] >= 0 && child[1] > 0 { if |queue| == 0 then 0 else var child := queue[0]; var stillNeeded := if child[1] <= child[0] then 0 else child[1] - child[0]; stillNeeded + SumCandiesStillNeeded(queue[1..]) } method solve(n: int, m: int, a: seq<int>) returns (result: int) requires ValidInput(n, m, a) ensures ValidResult(result, n)
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
