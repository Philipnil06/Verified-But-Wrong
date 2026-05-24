# External Vericoding Benchmark Audit

This patch adds an optional, soft-failing External Vericoding Benchmark Audit for the paper *Verified but Wrong: Intent-Gap Auditing for Vericoding Pipelines*.

## Data sources supported

Preferred order:

1. `external_data/vericoding-benchmark/jsonl/dafny_tasks.jsonl`
2. `external_data/vericoding/benchmarks/dafny_tasks.jsonl`
3. Git clone of `https://github.com/Beneficial-AI-Foundation/vericoding-benchmark`
4. Git clone of `https://github.com/Beneficial-AI-Foundation/vericoding`
5. Raw JSONL fallback from vericoding-benchmark
6. Raw JSONL fallback from vericoding

If all fail, the audit writes a skipped report and does not break the rest of reproduction.

## Commands

```bash
python external_vericoding_audit/fetch_external_benchmark.py --repo auto
python external_vericoding_audit/inspect_dafny_jsonl.py
python external_vericoding_audit/scan_target_validity_gaps.py
python external_vericoding_audit/make_manual_validation_pack.py --top 10
python external_vericoding_audit/validate_external_cases.py
python external_vericoding_audit/write_known_issue_context.py
python run_all_repro.py
```

## Manual validation rule

Scanner candidates are never validated automatically. A case is validated only if a human creates:

- `external_vericoding_cases/candidate_<id>/manual_validation.json`
- `bad_candidate.py`
- `intended_oracle.py`
- `weak_spec_proxy.py` or explicit documented manual proxy with `weak_spec_proxy_pass: true`

The validator reports `verified_but_wrong_demo: true` only when the adapted spec check passes and the intended oracle fails.

## Cautious framing

Use terms like:

- externally sourced target-validity gaps
- formal specs that appear weaker than NL/source intent
- adapted verified-but-wrong demonstrations
- not benchmark bug claims
- not vulnerability claims
- not prevalence estimates
