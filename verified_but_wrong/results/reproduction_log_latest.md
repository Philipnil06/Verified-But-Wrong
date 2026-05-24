# Reproduction Log

- timestamp: 2026-05-13T13:28:34.368667+00:00
- default LLM mode in reproduction: cached only

## Commands Run
- run_mini_benchmark: ok (artifact)
- run_policy_gate_calibration: ok (policy_gate_calibration)
- run_policy_gate_threshold_sweep: ok (policy_gate_threshold_sweep)
- run_repair_experiment: ok (spec_repair_experiment)
- run_repair_baselines: ok (spec_repair_baselines)
- run_defense_baselines: ok (defense_baselines)
- run_audit_gate_ablation: ok (audit_gate_ablation)
- run_candidate_set_underconstraint_analysis: ok (candidate_set_underconstraint)
- run_noisy_policy_pack_eval: ok (noisy_policy_pack_eval)
- run_naturalistic_experiment: ok (naturalistic_experiment)
- run_external_case_study: ok (external_case_study)
- run_external_issue_suite_eval: ok (external_issue_suite_eval)
- run_formal_demo: ok (formal_demo)
- run_llm_policy_split_eval: ok (llm_policy_split_eval)
- generate_policy_pack_index: ok (artifact)
- generate_provenance_table: ok (artifact)
- run_known_vs_unknown_policy_demo: ok (artifact)
- build_stats_summary: ok (artifact)
- run_optional_external_audit: ok (artifact)
- build_evidence_pack: ok (evidence_pack)
- write_final_submission_materials: ok (final_submission)
- write_results_sha256: ok (hashes)

## Reproduced Results
- tasks: see results/benchmark_latest.json
- dev tasks: 8
- heldout tasks: 4
- reports generated: benchmark, policy gate, threshold sweep, repair, repair baselines, defense baselines, ablation, candidate-set underconstraint, noisy policy-pack, naturalistic, external suite, formal demo, cached LLM policy-split, stats, provenance, evidence pack

## External Case Study
- case: kibana_role_downgrade_session_invalidation
- source: externally sourced public GitHub issue
- before repair verified_but_wrong: True
- gate result: BLOCK
- after repair verified_but_wrong: False

## External Vericoding Benchmark Audit
- status: ok
- validated cases: 7
- verified-but-wrong demos: 7
- paper-ready: True

## Final Summary

| Component | Status | Evidence-ready? |
|---|---|---|
| Candidate set | `passed` | yes |
| Noisy policy packs | `passed` | yes |
| External suite | `passed` | yes |
| External vericoding audit | `paper_ready` | yes |
| Formal demo | `skipped_dafny_not_installed` | no |
| LLM policy split | `partial_cached_coverage` | no |

## Files Generated
- results/benchmark_latest.json
- results/policy_gate_calibration_latest.json
- results/policy_gate_threshold_sweep.json
- results/spec_repair_latest.json
- results/spec_repair_baselines_latest.json
- results/defense_baselines_latest.json
- results/audit_gate_ablation_latest.json
- results/naturalistic_experiment_latest.json
- reports/candidate_set_underconstraint.json
- reports/noisy_policy_pack_eval.json
- reports/external_issue_suite_eval.json
- reports/formal_demo_result.json
- reports/llm_policy_split_eval.json
- reports/evidence_pack.md
- reports/paper_insert_llm_policy_split.md
- reports/paper_insert_formal_demo.md
- results/stats_summary.json
- results/provenance_table.json
- ../external_case_studies/kibana_role_downgrade_session_invalidation/results.json
- ../external_case_studies/kibana_role_downgrade_session_invalidation/external_case_report.md
- RESULTS_SHA256.txt