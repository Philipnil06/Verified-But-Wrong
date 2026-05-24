# Bounded Attempt: Additional Tier 1 Direct-Dafny Case

## Summary
- Attempted `DA0157` first; bounded direct verification timed out.
- Promoted `DA0293` to Tier 1 direct-Dafny with complete evidence chain.

## DA0157
- Result: not promoted in bounded run.
- Reason: verifier timeout.

## DA0293
- Original target verification: success (`0 errors`).
- Intended examples: bad candidate fails examples.
- Repaired-target check: blocks same bad candidate.

## Conservative Paper Delta
1. Increase direct-Dafny cases from 2 to 3.
2. Add DA0293 as a third direct-Dafny existence case.
3. Do not change any prevalence claims.
