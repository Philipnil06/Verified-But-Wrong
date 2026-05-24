# External Vericoding Benchmark Audit — Not Paper-Ready Yet

Validated verified-but-wrong demos: **0**.

This external audit should not be presented as a paper-ready results section until at least 3 manually defensible cases are validated.

## Next steps

1. Review `reports/external_vericoding_gap_candidates.md` and choose 3–5 strong cases.
2. For each case, inspect the full NL/source intent and Dafny spec.
3. Write `manual_validation.json`, `bad_candidate.py`, `weak_spec_proxy.py` if executable, and task-specific `intended_oracle.py`.
4. Re-run `python external_vericoding_audit/validate_external_cases.py`.

## Cautious interpretation

Candidate gaps are not benchmark bug claims, vulnerability claims, or prevalence estimates.
