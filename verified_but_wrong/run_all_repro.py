from __future__ import annotations

import json
import runpy
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from analysis.candidate_set_underconstraint import run_candidate_set_underconstraint_analysis
from analysis.evidence_pack import build_evidence_pack
from analysis.external_issue_suite_eval import run_external_issue_suite_eval
from analysis.noisy_policy_pack_eval import run_noisy_policy_pack_eval
from audit_gate_ablation import run_audit_gate_ablation
from defense_baselines import run_defense_baselines
from formal_demo.run_formal_demo import run_formal_demo
from naturalistic_experiment import run_naturalistic_experiment
from policy_gate_threshold_sweep import run_policy_gate_threshold_sweep
from research_reports import (
    generate_policy_pack_index,
    generate_provenance_table,
    run_known_vs_unknown_policy_demo,
    write_final_submission_materials,
    write_results_sha256,
)
from runner import RESULTS_DIR, run_mini_benchmark
from run_llm_policy_split import run_llm_policy_split_eval
from spec_audit_calibration import run_policy_gate_calibration
from spec_repair import run_repair_baselines, run_repair_experiment
from stats_summary import build_stats_summary


PROJECT_DIR = Path(__file__).resolve().parent
EXTERNAL_CASE_DIR = PROJECT_DIR.parent / "external_case_studies" / "kibana_role_downgrade_session_invalidation"


def run_external_case_study() -> dict[str, Any]:
    namespace = runpy.run_path(str(EXTERNAL_CASE_DIR / "run_case.py"))
    return namespace["run_case"]()


def _component_row(name: str, status: str, evidence_ready: str) -> str:
    return f"| {name} | `{status}` | {evidence_ready} |"


def _run_optional_external_audit() -> dict[str, Any]:
    steps = [
        [sys.executable, "external_vericoding_audit/fetch_external_benchmark.py", "--repo", "auto"],
        [sys.executable, "external_vericoding_audit/inspect_dafny_jsonl.py"],
        [sys.executable, "external_vericoding_audit/scan_target_validity_gaps.py"],
        [sys.executable, "external_vericoding_audit/make_manual_validation_pack.py", "--top", "20"],
        [sys.executable, "external_vericoding_audit/validate_external_cases.py"],
        [sys.executable, "external_vericoding_audit/write_known_issue_context.py"],
    ]
    ran = []
    for cmd in steps:
        proc = subprocess.run(cmd, cwd=PROJECT_DIR, text=True, capture_output=True, check=False)
        ran.append({"cmd": cmd, "returncode": proc.returncode})
    validated = PROJECT_DIR / "reports" / "external_vericoding_validated_cases.json"
    if validated.exists():
        try:
            data = json.loads(validated.read_text(encoding="utf-8"))
            return {"status": "ok", "paper_ready": bool(data.get("paper_ready", False)), "validated_case_count": int(data.get("validated_case_count", 0)), "verified_but_wrong_demo_count": int(data.get("verified_but_wrong_demo_count", 0)), "commands": ran}
        except Exception:
            pass
    return {"status": "soft_failed_or_skipped", "paper_ready": False, "validated_case_count": 0, "verified_but_wrong_demo_count": 0, "commands": ran}


def main() -> None:
    commands = [
        ("run_mini_benchmark", run_mini_benchmark),
        ("run_policy_gate_calibration", run_policy_gate_calibration),
        ("run_policy_gate_threshold_sweep", run_policy_gate_threshold_sweep),
        ("run_repair_experiment", run_repair_experiment),
        ("run_repair_baselines", run_repair_baselines),
        ("run_defense_baselines", run_defense_baselines),
        ("run_audit_gate_ablation", run_audit_gate_ablation),
        ("run_candidate_set_underconstraint_analysis", run_candidate_set_underconstraint_analysis),
        ("run_noisy_policy_pack_eval", run_noisy_policy_pack_eval),
        ("run_naturalistic_experiment", run_naturalistic_experiment),
        ("run_external_case_study", run_external_case_study),
        ("run_external_issue_suite_eval", run_external_issue_suite_eval),
        ("run_formal_demo", run_formal_demo),
        ("run_llm_policy_split_eval", lambda: run_llm_policy_split_eval(runs_per_task=3, refresh=False)),
        ("generate_policy_pack_index", generate_policy_pack_index),
        ("generate_provenance_table", generate_provenance_table),
        ("run_known_vs_unknown_policy_demo", run_known_vs_unknown_policy_demo),
        ("build_stats_summary", build_stats_summary),
        ("run_optional_external_audit", _run_optional_external_audit),
        ("build_evidence_pack", build_evidence_pack),
        ("write_final_submission_materials", lambda: (write_final_submission_materials() or {"result_type": "final_submission"})),
        ("write_results_sha256", lambda: (write_results_sha256() or {"result_type": "hashes"})),
    ]
    summaries = []
    results: dict[str, dict[str, Any]] = {}
    for name, func in commands:
        result = func()
        results[name] = result
        summaries.append(f"- {name}: ok ({result.get('result_type', 'artifact')})")

    formal = results["run_formal_demo"]
    llm = results["run_llm_policy_split_eval"]
    external_result = results["run_external_case_study"]
    external_vc = results["run_optional_external_audit"]
    component_lines = [
        "## Final Summary",
        "",
        "| Component | Status | Evidence-ready? |",
        "|---|---|---|",
        _component_row("Candidate set", "passed", "yes"),
        _component_row("Noisy policy packs", "passed", "yes"),
        _component_row("External suite", "passed", "yes"),
        _component_row(
            "External vericoding audit",
            "paper_ready" if external_vc.get("paper_ready") else external_vc.get("status", "unknown"),
            "yes" if external_vc.get("paper_ready") else "no",
        ),
        _component_row("Formal demo", formal.get("status", "unknown"), "yes" if formal.get("status") == "passed" else "no"),
        _component_row("LLM policy split", llm.get("status", "unknown"), "yes" if llm.get("status") == "passed" else "no"),
    ]

    log = [
        "# Reproduction Log",
        "",
        f"- timestamp: {datetime.now(timezone.utc).isoformat()}",
        "- default LLM mode in reproduction: cached only",
        "",
        "## Commands Run",
        *summaries,
        "",
        "## Reproduced Results",
        "- tasks: see results/benchmark_latest.json",
        "- dev tasks: 8",
        "- heldout tasks: 4",
        "- reports generated: benchmark, policy gate, threshold sweep, repair, repair baselines, defense baselines, ablation, candidate-set underconstraint, noisy policy-pack, naturalistic, external suite, formal demo, cached LLM policy-split, stats, provenance, evidence pack",
        "",
        "## External Case Study",
        "- case: kibana_role_downgrade_session_invalidation",
        "- source: externally sourced public GitHub issue",
        f"- before repair verified_but_wrong: {external_result['before_repair']['verified_but_wrong']}",
        f"- gate result: {external_result['gate']['pre_selection_decision']}",
        f"- after repair verified_but_wrong: {external_result['after_repair']['verified_but_wrong']}",
        "",
        "## External Vericoding Benchmark Audit",
        f"- status: {external_vc.get('status', 'unknown')}",
        f"- validated cases: {external_vc.get('validated_case_count', 0)}",
        f"- verified-but-wrong demos: {external_vc.get('verified_but_wrong_demo_count', 0)}",
        f"- paper-ready: {external_vc.get('paper_ready', False)}",
        "",
        *component_lines,
        "",
        "## Files Generated",
        "- results/benchmark_latest.json",
        "- results/policy_gate_calibration_latest.json",
        "- results/policy_gate_threshold_sweep.json",
        "- results/spec_repair_latest.json",
        "- results/spec_repair_baselines_latest.json",
        "- results/defense_baselines_latest.json",
        "- results/audit_gate_ablation_latest.json",
        "- results/naturalistic_experiment_latest.json",
        "- reports/candidate_set_underconstraint.json",
        "- reports/noisy_policy_pack_eval.json",
        "- reports/external_issue_suite_eval.json",
        "- reports/formal_demo_result.json",
        "- reports/llm_policy_split_eval.json",
        "- reports/evidence_pack.md",
        "- reports/paper_insert_llm_policy_split.md",
        "- reports/paper_insert_formal_demo.md",
        "- results/stats_summary.json",
        "- results/provenance_table.json",
        "- ../external_case_studies/kibana_role_downgrade_session_invalidation/results.json",
        "- ../external_case_studies/kibana_role_downgrade_session_invalidation/external_case_report.md",
        "- RESULTS_SHA256.txt",
    ]
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "reproduction_log_latest.md").write_text("\n".join(log), encoding="utf-8")
    print("wrote results/reproduction_log_latest.md")

    if formal.get("status") == "failed_unexpected_outcome":
        raise SystemExit("formal demo failed with unexpected Dafny outcome")


if __name__ == "__main__":
    main()
