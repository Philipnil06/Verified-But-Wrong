# External Vericoding Integration Notes

## Integration status

The patch was hardened in this patch folder, but the real repository was not mounted in the execution environment. Therefore no existing repository files were actually modified.

## Files added in the patch bundle

- `external_vericoding_audit/common.py`
- `external_vericoding_audit/fetch_external_benchmark.py`
- `external_vericoding_audit/inspect_dafny_jsonl.py`
- `external_vericoding_audit/scan_target_validity_gaps.py`
- `external_vericoding_audit/make_manual_validation_pack.py`
- `external_vericoding_audit/validate_external_cases.py`
- `external_vericoding_audit/write_known_issue_context.py`
- `external_vericoding_cases/validated_cases.example.json`
- `README_external_vericoding_audit.md`
- `reports/external_vericoding_integration_notes.md`

## Existing files that would need manual merge in the real repo

- `run_all_repro.py`
- `analysis/evidence_pack.py`
- `README.md`

The versions in this patch bundle are reference implementations. Do not overwrite existing files blindly. Merge the external audit steps into the existing runner and merge the external evidence section into the existing evidence pack.

## Manual merge decisions encoded

- External data fetch is optional and soft-failing.
- Both public dataset schemas are supported.
- Scanner output is candidate-only.
- Manual validation is required before any case appears as a VBW demo.
- Paper insert is conditional: fewer than 3 validated demos produces a not-paper-ready report.

## Risks

- The scanner is heuristic and may produce false positives.
- Generated validation packs are not evidence until a human writes task-specific oracles.
- Python proxy demos are not full Dafny re-verification.
- If the real repo has a custom runner/evidence pack, merge conflicts must be resolved manually.
