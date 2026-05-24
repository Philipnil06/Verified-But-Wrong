# DA0293 Tier 1 Direct-Dafny Promotion Check

## Outcome
- **Qualifies as Tier 1 direct-Dafny:** Yes
- Dafny version: `4.11.0`
- Original-target verification: `Dafny program verifier finished with 3 verified, 0 errors`
- Intended examples against same bad candidate: all fail (`expected != 0` on all listed cases)
- Repaired-target check: blocked (`assertion might not hold`)

## Evidence Files
- `external_vericoding_cases/candidate_DA0293/dafny_direct/bad_candidate.dfy`
- `external_vericoding_cases/candidate_DA0293/dafny_direct/verify_stdout.txt`
- `external_vericoding_cases/candidate_DA0293/dafny_direct/intended_examples_result.json`
- `external_vericoding_cases/candidate_DA0293/dafny_repaired/bad_candidate_repaired_target.dfy`
- `external_vericoding_cases/candidate_DA0293/dafny_repaired/verify_stdout.txt`

## Claim Scope
This is a single additional direct-Dafny verified-but-wrong demonstration. It does not support any broader prevalence claim.
