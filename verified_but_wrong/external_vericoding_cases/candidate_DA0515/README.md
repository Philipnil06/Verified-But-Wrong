# External Vericoding Candidate DA0515

Status: **candidate_needs_manual_oracle**

Source: `apps`  
Source id: `apps_test_4267`  
Gap category: `trivial_postcondition`  
Confidence: `high`

## NL intent excerpt

```text
Given a room temperature in degrees Celsius, determine whether to turn on an air conditioner. The air conditioner should be turned on if and only if the temperature is 30°C or higher.
```

## Formal spec excerpt

```dafny
predicate ValidTemperature(temp: int) { -40 <= temp <= 40 } function ExpectedOutput(temp: int): string { if temp >= 30 then "Yes\n" else "No\n" } predicate CorrectOutput(temp: int, output: string) { output == ExpectedOutput(temp) } method solve(X: int) returns (result: string) requires ValidTemperature(X) ensures CorrectOutput(X, result)
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

## Caveat

This is an adapted demonstration candidate, not a benchmark bug claim, not a real-world vulnerability claim, and not a prevalence estimate.
