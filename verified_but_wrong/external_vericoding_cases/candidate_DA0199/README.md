# External Vericoding Candidate DA0199

Status: **candidate_auto_pack_created_needs_manual_oracle**

Source: `apps`  
Source id: `apps_test_985`  
Gap category: `trivial_postcondition`  
Confidence: `high`

## NL intent excerpt

```text
Given n bishops on a 1000×1000 grid, count the number of pairs that attack each other. Two bishops attack each other if and only if they are on the same diagonal (either main diagonal or anti-diagonal). Main diagonal: x - y is constant, Anti-diagonal: x + y is constant.
```

## Formal spec excerpt

```dafny
predicate ValidInput(positions: seq<(int, int)>) { |positions| >= 1 && |positions| <= 200000 && (forall i :: 0 <= i < |positions| ==> 1 <= positions[i].0 <= 1000 && 1 <= positions[i].1 <= 1000) && (forall i, j :: 0 <= i < j < |positions| ==> positions[i] != positions[j]) } function CountAttackingPairs(positions: seq<(int, int)>): int requires ValidInput(positions) { |set i, j | 0 <= i < j < |positions| && (positions[i].0 + positions[i].1 == positions[j].0 + positions[j].1 || positions[i].0 - positions[i].1 == positions[j].0 - positions[j].1) :: (i, j)| } predicate ValidOutput(positions: seq<(int, int)>, result: int) requires ValidInput(positions) { result == CountAttackingPairs(positions) && result >= 0 } method SolveBishops(positions: seq<(int, int)>) returns (result: int) requires ValidInput(positions) ensures ValidOutput(positions, result) ensures result >= 0
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
