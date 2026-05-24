# Gap Analysis: DA0315

Status: **candidate only, not validated**.

Source: `apps` / `apps_test_1618`
Category: `trivial_postcondition`
Confidence: `high`

## Suspected missing requirement

semantic correctness condition

## Why the formal spec may be weak

formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only

## Candidate bad implementation idea

return a range/shape-valid but semantically wrong value

## NL excerpt

```text
Given a staircase with n stairs at non-decreasing heights, process m boxes thrown sequentially. Each box has width w and height h, covering stairs 1 through w. A box falls until its bottom touches either a stair top or a previously placed box top within its coverage area. Determine the landing height of each box's bottom.
```

## Formal spec excerpt

```dafny
function max(a: int, b: int): int { if a >= b then a else b } predicate ValidStairs(stair_heights: seq<int>) { |stair_heights| >= 1 && (forall i :: 0 <= i < |stair_heights| - 1 ==> stair_heights[i] <= stair_heights[i + 1]) && (forall i :: 0 <= i < |stair_heights| ==> stair_heights[i] >= 0) } predicate ValidBoxes(boxes: seq<(int, int)>, stairs_amount: int) { forall i :: 0 <= i < |boxes| ==> boxes[i].0 >= 1 && boxes[i].0 <= stairs_amount && boxes[i].1 >= 1 } predicate ValidResult(result: seq<int>, boxes: seq<(int, int)>, stair_heights: seq<int>) requires |stair_heights| >= 1 requires forall i :: 0 <= i < |boxes| ==> boxes[i].0 >= 1 && boxes[i].0 <= |stair_heights| { |result| == |boxes| && (forall i :: 0 <= i < |boxes| ==> result[i] >= 0) && (forall i :: 0 <= i < |boxes| ==> result[i] >= stair_heights[0] && result[i] >= stair_heights[boxes[i].0 - 1]) && (forall i :: 0 <= i < |boxes| ==> result[i] == max(if i == 0 then stair_heights[0] else result[i-1] + boxes[i-1].1, stair_heights[boxes[i].0 - 1])) } method solve(stairs_amount: int, stair_heights: seq<int>, boxes_amount: int, boxes:...
```

## Required manual work

A human must inspect the full external task, write a task-specific weak-spec proxy or document the exact proxy, write an intended oracle over selected inputs, and then create manual_validation.json with status validated or rejected.

Caveat: this is an adapted target-validity demonstration candidate, not a benchmark bug claim.