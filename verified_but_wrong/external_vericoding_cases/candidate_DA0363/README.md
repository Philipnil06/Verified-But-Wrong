# External Vericoding Candidate DA0363

Status: **candidate_needs_manual_oracle**

Source: `apps`  
Source id: `apps_test_1886`  
Gap category: `trivial_postcondition`  
Confidence: `high`

## NL intent excerpt

```text
Given a non-empty word consisting of lowercase and uppercase English letters, capitalize the first letter while keeping all other letters unchanged.
```

## Formal spec excerpt

```dafny
predicate ValidInput(word: string) { |word| > 0 && forall i :: 0 <= i < |word| ==> ('a' <= word[i] <= 'z') || ('A' <= word[i] <= 'Z') } predicate CorrectCapitalization(input: string, output: string) requires ValidInput(input) { |output| == |input| && ('A' <= output[0] <= 'Z') && (('a' <= input[0] <= 'z') ==> ('A' <= output[0] <= 'Z')) && (('A' <= input[0] <= 'Z') ==> (output[0] == input[0])) && forall i :: 1 <= i < |input| ==> output[i] == input[i] }
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
