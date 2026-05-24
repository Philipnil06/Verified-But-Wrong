# DA0003 Walkthrough (Externally Sourced Target-Validity Demo)

For DA0003, we additionally implemented a trivially wrong Dafny candidate that verifies directly against the original benchmark target while failing intended-behavior examples.

## Direct Dafny execution details

- Dafny version: `4.11.0+fcb2042d6d043a2634f0854338c08feeaaaf4ae2`
- Verify command:
  - `dotnet tool run dafny verify external_vericoding_cases/candidate_DA0003/dafny_direct/bad_candidate.dfy`
- Verifier output summary:
  - `Dafny program verifier finished with 2 verified, 0 errors`
- Verification return code: `0`

## Original target excerpt

```dafny
method solve(...) returns (result: int)
  ...
  ensures result >= 0
```

## Bad candidate excerpt

```dafny
method solve(...) returns (result: int) {
  return 0;
}
```

## Intended examples

Expected outputs:

```text
(5,2,3,4,5) -> 13
(10,2,5,3,8) -> 28
(12,3,4,7,2) -> 32
```

Bad candidate outputs:

```text
0
0
0
```

## Cautious interpretation

This is one direct-Dafny verified case against the original external benchmark target. It is not a prevalence estimate, not a benchmark-bug claim, and not a vulnerability claim.
