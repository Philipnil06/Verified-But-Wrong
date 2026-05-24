# External Vericoding Candidate DA0045

Status: **candidate_auto_pack_created_needs_manual_oracle**

Source: `apps`  
Source id: `apps_test_181`  
Gap category: `trivial_postcondition`  
Confidence: `high`

## NL intent excerpt

```text
Given a camera rotation angle in degrees, determine the minimum number of 90-degree clockwise rotations needed to minimize the image's deviation from vertical orientation. When a camera rotates by x degrees, the image appears rotated by -x degrees.
```

## Formal spec excerpt

```dafny
function NormalizeAngle(angle: int): int { var n := angle % 360; if n < 0 then n + 360 else n } function DeviationFromVertical(angle: int): int requires 0 <= angle < 360 { if angle <= 180 then angle else 360 - angle } function ImageAngleAfterRotations(cameraAngle: int, rotations: int): int requires 0 <= rotations <= 3 { NormalizeAngle(-cameraAngle + 90 * rotations) } function ImageDeviationAfterRotations(cameraAngle: int, rotations: int): int requires 0 <= rotations <= 3 { DeviationFromVertical(ImageAngleAfterRotations(cameraAngle, rotations)) } predicate IsOptimalRotations(cameraAngle: int, result: int) requires 0 <= result <= 3 { forall k :: 0 <= k <= 3 ==> var result_deviation := ImageDeviationAfterRotations(cameraAngle, result); var k_deviation := ImageDeviationAfterRotations(cameraAngle, k); result_deviation < k_deviation || (result_deviation == k_deviation && result <= k) } method solve(x: int) returns (result: int) ensures 0 <= result <= 3 ensures IsOptimalRotations(x, result)
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
