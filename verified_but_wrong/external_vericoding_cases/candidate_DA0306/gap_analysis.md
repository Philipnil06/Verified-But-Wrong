# Gap Analysis: DA0306

Status: **candidate only, not validated**.

Source: `apps` / `apps_test_1576`
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
Decrypt a string that was encrypted using the Right-Left cipher. The Right-Left cipher encrypts by starting with the first character, then alternating between appending to the right (even positions) and prepending to the left (odd positions) for subsequent characters.
```

## Formal spec excerpt

```dafny
predicate ValidInput(t: string) { |t| >= 1 } method solve(t: string) returns (result: string) requires ValidInput(t) ensures |result| == |t|
```

## Required manual work

A human must inspect the full external task, write a task-specific weak-spec proxy or document the exact proxy, write an intended oracle over selected inputs, and then create manual_validation.json with status validated or rejected.

Caveat: this is an adapted target-validity demonstration candidate, not a benchmark bug claim.