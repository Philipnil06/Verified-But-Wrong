# External VBW Replication Implementation Plan

## Scope
Build an additive scanner-ranked external replication suite integrated with the existing external vericoding audit assets, without overwriting prior paper outputs or previous result files.

## Discovered Relevant Files
- External scanner outputs and inspection
  - `reports/external_vericoding_gap_candidates.json`
  - `reports/external_vericoding_gap_candidates.md`
  - `reports/external_vericoding_inspection.json`
  - `reports/external_vericoding_inspection.md`
  - `reports/external_vericoding_inspection_log.json`
  - `reports/external_vericoding_rejection_reasons.md`
- Existing validated/manual external case evidence
  - `reports/external_vericoding_validated_cases.json`
  - `reports/external_vericoding_validated_cases.md`
  - `external_vericoding_cases/candidate_*/manual_validation.json`
  - `external_vericoding_cases/candidate_*/manual_validation.template.json`
- Existing direct-Dafny evidence (current Tier 1)
  - `external_vericoding_audit/run_direct_dafny_cases.py`
  - `reports/external_vericoding_direct_dafny.json`
  - `reports/external_vericoding_direct_dafny.md`
  - `external_vericoding_cases/candidate_DA0003/dafny_direct/*`
  - `external_vericoding_cases/candidate_DA0208/dafny_direct/*`
- Benchmark data / reconstruction source
  - `external_data/vericoding-benchmark/jsonl/dafny_tasks.jsonl`
- Reproduction entrypoints and paper artifacts
  - `run_all_repro.py`
  - `analysis/evidence_pack.py`
  - `README.md`
  - `RESULTS_SHA256.txt`

## Existing Pipeline Entrypoints
- `run_all_repro.py` already runs optional external vericoding audit and writes reports.
- `external_vericoding_audit/*.py` provides fetch, inspect, scan, manual pack, validate, and known-issue context generation.
- `external_vericoding_audit/run_direct_dafny_cases.py` currently verifies DA0003 and DA0208 direct-Dafny attempts.

## Proposed New Scripts
- `scripts/external_replication/build_high_confidence_inventory.py`
- `scripts/external_replication/adjudicate_high_confidence.py`
- `scripts/external_replication/run_dafny_external_cases.py`
- `scripts/external_replication/run_repaired_target_checks.py`
- `scripts/external_replication/run_intended_examples.py`
- `scripts/external_replication/random_control_sample.py`
- `scripts/external_replication/make_external_replication_tables.py`
- `run_external_replication.py`

## Proposed New Protocol/Docs
- `EXTERNAL_REPLICATION_PROTOCOL.md`
- `paper_assets/external_replication_paper_insert.md`

## Proposed Output Paths
- `results/external_replication/high_confidence_inventory.jsonl`
- `results/external_replication/high_confidence_inventory.csv`
- `results/external_replication/high_confidence_summary.json`
- `results/external_replication/adjudication.jsonl`
- `results/external_replication/adjudication_template_remaining.csv`
- `results/external_replication/dafny_logs/*`
- `results/external_replication/dafny_direct_summary.{jsonl,csv,md}`
- `results/external_replication/repaired_target_summary.{jsonl,csv,md}`
- `results/external_replication/intended_examples_summary.{jsonl,csv,md}`
- `results/external_replication/random_control_*.{jsonl,md}` (optional)
- `results/external_replication/README.md`
- `paper_assets/external_replication_summary_table.md`
- `paper_assets/external_replication_cases_table.md`
- `paper_assets/external_replication_repair_table.md`
- `paper_assets/evidence_stack_figure_data.json`
- `paper_assets/evidence_stack_figure.md`
- `paper_assets/evidence_stack_figure.png`
- `paper_assets/evidence_stack_figure.svg`

## Assumptions
- Canonical candidate source is `reports/external_vericoding_gap_candidates.json` with `confidence == high` for the 41 high-confidence candidates.
- External benchmark record reconstruction uses `external_data/vericoding-benchmark/jsonl/dafny_tasks.jsonl` fields: `id`, `source`, `source-id`, `vc-description`, `vc-preamble`, `vc-spec`.
- Existing `manual_validation.json` and case-level notes are treated as prior evidence for conservative prefill only.
- Local Dafny execution is via `dotnet tool run dafny ...` using existing `.config/dotnet-tools.json`.

## Risks
- Some candidate metadata fields are inconsistent across historical outputs; inventory script must record reconstruction method explicitly.
- Non-trivial direct-Dafny replications (e.g., DA0157/DA0010) may be difficult to prove in limited time; attempts must be logged and labeled conservatively.
- Repaired-target checks can demonstrate mechanism blocking but may be example-level rather than full formal repair; wording must avoid overclaims.
- Optional control sample may remain incomplete and should not block main pipeline.
