# External Vericoding Integration Notes

## Files added

- `external_vericoding_audit/common.py`
- `external_vericoding_audit/fetch_external_benchmark.py`
- `external_vericoding_audit/inspect_dafny_jsonl.py`
- `external_vericoding_audit/scan_target_validity_gaps.py`
- `external_vericoding_audit/make_manual_validation_pack.py`
- `external_vericoding_audit/validate_external_cases.py`
- `external_vericoding_audit/write_known_issue_context.py`
- `external_vericoding_cases/validated_cases.example.json`
- `README_external_vericoding_audit.md`
- `integrate_external_vericoding_patch.py`
- `reports/external_vericoding_integration_notes.md`

## Existing files modified

- `run_all_repro.py`
- `analysis/evidence_pack.py`
- `README.md`

## Files skipped from patch bundle

- `README.md` (reference version skipped; merged additions only)
- `run_all_repro.py` (reference version skipped; merged additions only)
- `analysis/evidence_pack.py` (reference version skipped; merged additions only)
- `analysis/__pycache__/*.pyc` and `__pycache__/*.pyc`
- Patch-provided `reports/external_vericoding_*.json|.md` and `reports/paper_insert_external_vericoding_audit.md` (not copied; regenerated in this repo)

## run_all_repro.py merge approach

- Kept all existing internal reproduction commands unchanged.
- Added a new optional `_run_optional_external_audit()` block that runs:
  1. `fetch_external_benchmark.py --repo auto`
  2. `inspect_dafny_jsonl.py`
  3. `scan_target_validity_gaps.py`
  4. `make_manual_validation_pack.py --top 20`
  5. `validate_external_cases.py`
  6. `write_known_issue_context.py`
- Added external-audit summary rows to final reproduction log.
- External block is soft-failing and does not stop internal reproduction.
- Ordered external block before `build_evidence_pack` so evidence pack includes fresh external status.

## analysis/evidence_pack.py merge approach

- Kept existing evidence sections intact.
- Added `External Vericoding Benchmark Audit` section with:
  - data status
  - dataset schema/path
  - commit/hash
  - inspected record count
  - useful NL count
  - candidate count
  - validated case count
  - paper-ready flag
  - caveat text

## Caveats

- No validated external cases yet (`validated_case_count = 0`), so paper insert is currently non-paper-ready.
- Some path strings emitted by tools include mojibake for the OneDrive parent folder name; actual filesystem paths are still valid and executable.
