# Gap Analysis: DA0199

Status: **candidate only, not validated**.

Source: `apps` / `apps_test_985`
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
Given n bishops on a 1000×1000 grid, count the number of pairs that attack each other. Two bishops attack each other if and only if they are on the same diagonal (either main diagonal or anti-diagonal). Main diagonal: x - y is constant, Anti-diagonal: x + y is constant.
```

## Formal spec excerpt

```dafny
predicate ValidInput(positions: seq<(int, int)>) { |positions| >= 1 && |positions| <= 200000 && (forall i :: 0 <= i < |positions| ==> 1 <= positions[i].0 <= 1000 && 1 <= positions[i].1 <= 1000) && (forall i, j :: 0 <= i < j < |positions| ==> positions[i] != positions[j]) } function CountAttackingPairs(positions: seq<(int, int)>): int requires ValidInput(positions) { |set i, j | 0 <= i < j < |positions| && (positions[i].0 + positions[i].1 == positions[j].0 + positions[j].1 || positions[i].0 - positions[i].1 == positions[j].0 - positions[j].1) :: (i, j)| } predicate ValidOutput(positions: seq<(int, int)>, result: int) requires ValidInput(positions) { result == CountAttackingPairs(positions) && result >= 0 } method SolveBishops(positions: seq<(int, int)>) returns (result: int) requires ValidInput(positions) ensures ValidOutput(positions, result) ensures result >= 0
```

## Required manual work

A human must inspect the full external task, write a task-specific weak-spec proxy or document the exact proxy, write an intended oracle over selected inputs, and then create manual_validation.json with status validated or rejected.

Caveat: this is an adapted target-validity demonstration candidate, not a benchmark bug claim.