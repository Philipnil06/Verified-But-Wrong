# Gap Analysis: DA0136

Status: **candidate only, not validated**.

Source: `apps` / `apps_test_682`
Category: `trivial_postcondition`
Confidence: `high`

## Suspected missing requirement

semantic correctness condition

## Why the formal spec may be weak

formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only; spec has few semantic-strength tokens

## Candidate bad implementation idea

return a range/shape-valid but semantically wrong value

## NL excerpt

```text
Given starting position (r1, c1) and ending position (r2, c2) on an 8×8 chessboard, find the minimum number of moves required for a rook, bishop, and king to move from the starting position to the ending position. Return 0 if a piece cannot reach the destination.
```

## Formal spec excerpt

```dafny
predicate ValidPosition(r: int, c: int) { 1 <= r <= 8 && 1 <= c <= 8 } function RookMoves(r1: int, c1: int, r2: int, c2: int): int requires ValidPosition(r1, c1) && ValidPosition(r2, c2) { if r1 == r2 && c1 == c2 then 0 else if r1 == r2 || c1 == c2 then 1 else 2 } function BishopMoves(r1: int, c1: int, r2: int, c2: int): int requires ValidPosition(r1, c1) && ValidPosition(r2, c2) { if r1 == r2 && c1 == c2 then 0 else var row_diff := if r1 >= r2 then r1 - r2 else r2 - r1; var col_diff := if c1 >= c2 then c1 - c2 else c2 - c1; if row_diff == col_diff then 1 else if (r1 + c1) % 2 == (r2 + c2) % 2 then 2 else 0 } function KingMoves(r1: int, c1: int, r2: int, c2: int): int requires ValidPosition(r1, c1) && ValidPosition(r2, c2) { var row_diff := if r1 >= r2 then r1 - r2 else r2 - r1; var col_diff := if c1 >= c2 then c1 - c2 else c2 - c1; if row_diff >= col_diff then row_diff else col_diff } predicate ValidResult(result: seq<int>, r1: int, c1: int, r2: int, c2: int) requires ValidPosition(r1, c1) && ValidPosition(r2, c2) { |result| == 3 && result[0] == RookMoves(r1, c1, r2, c2) && resul...
```

## Required manual work

A human must inspect the full external task, write a task-specific weak-spec proxy or document the exact proxy, write an intended oracle over selected inputs, and then create manual_validation.json with status validated or rejected.

Caveat: this is an adapted target-validity demonstration candidate, not a benchmark bug claim.