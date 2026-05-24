from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from analysis.common import REPORTS_DIR, result_path, write_markdown


def _load_result_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _llm_table_lines(llm: dict[str, Any]) -> list[str]:
    lines = [
        "## LLM Policy-Split",
        f"- status: {llm.get('status', 'MISSING')}",
    ]
    summaries = llm.get("summaries", [])
    if summaries:
        for row in summaries:
            lines.append(
                f"- {row['condition']}: valid={row['valid_specs']}, omitted causal={row['causal_policy_omitted_count']}, selected VBW={row['selected_vbw_count']}"
            )
    else:
        lines.append("- no cached or live generated specs were available")
    return lines


def _formal_table_lines(formal: dict[str, Any]) -> list[str]:
    lines = ["## Formal Demo", f"- status: {formal.get('status', 'MISSING')}"]
    for check in formal.get("checks", []):
        lines.append(
            f"- {check['name']}: expected={check['expected_outcome']}, actual={check['actual_outcome']}, result={check['result']}"
        )
    return lines


def _external_vericoding_lines() -> list[str]:
    fetch = _load_result_json(REPORTS_DIR / "external_vericoding_fetch.json") or {}
    inspect = _load_result_json(REPORTS_DIR / "external_vericoding_inspection.json") or {}
    scan = _load_result_json(REPORTS_DIR / "external_vericoding_gap_candidates.json") or {}
    validated = _load_result_json(REPORTS_DIR / "external_vericoding_validated_cases.json") or {}
    dataset = fetch.get("dataset") or inspect.get("dataset") or {}
    return [
        "## External Vericoding Benchmark Audit",
        f"- data status: {fetch.get('status', 'unknown')}",
        f"- dataset schema/path: {dataset.get('jsonl_path', inspect.get('jsonl_path', 'unknown'))}",
        f"- commit/hash: {dataset.get('commit_hash', 'unknown')}",
        f"- records inspected: {inspect.get('total_records', 'unknown')}",
        f"- useful NL descriptions: {inspect.get('total_with_useful_description', 'unknown')}",
        f"- candidate gaps: {scan.get('candidate_count', 'unknown')}",
        f"- validated cases: {validated.get('validated_case_count', 0)}",
        f"- paper-ready: {validated.get('paper_ready', False)}",
        "- caveat: candidate scan is not validation and not a prevalence estimate.",
    ]


def build_evidence_pack() -> dict[str, Any]:
    benchmark = _load_result_json(result_path("benchmark_latest.json")) or {}
    gate = _load_result_json(result_path("policy_gate_calibration_latest.json")) or {}
    repair = _load_result_json(result_path("spec_repair_baselines_latest.json")) or {}
    under = _load_result_json(REPORTS_DIR / "candidate_set_underconstraint.json") or {}
    noisy = _load_result_json(REPORTS_DIR / "noisy_policy_pack_eval.json") or {}
    external = _load_result_json(REPORTS_DIR / "external_issue_suite_eval.json") or {}
    formal = _load_result_json(REPORTS_DIR / "formal_demo_result.json") or {}
    llm = _load_result_json(REPORTS_DIR / "llm_policy_split_eval.json") or {}

    lines = [
        "# Evidence Pack",
        "",
        "## Main Benchmark",
        f"- executable tasks: {benchmark.get('naive', {}).get('total_tasks', 'MISSING')}",
        f"- naive VBW: {benchmark.get('naive', {}).get('wrong_selections', 'MISSING')}/{benchmark.get('naive', {}).get('total_tasks', 'MISSING')}",
        f"- critic VBW: {benchmark.get('critic', {}).get('wrong_selections', 'MISSING')}/{benchmark.get('critic', {}).get('total_tasks', 'MISSING')}",
        f"- oracle VBW: {benchmark.get('oracle', {}).get('wrong_selections', 'MISSING')}/{benchmark.get('oracle', {}).get('total_tasks', 'MISSING')}",
        "",
        "## Candidate-Set Underconstraint",
    ]
    for row in under.get("aggregate", []):
        lines.append(
            f"- {row['spec_mode']}: mean risk={row['mean_underconstraint_risk']:.2f}, "
            f"existence risk tasks={row['tasks_with_existence_risk']}/{row['tasks']}, selected VBW={row['selected_vbw_count']}/{row['tasks']}"
        )
    lines.extend(
        [
            "",
            "## Gate Calibration",
            f"- dangerous caught: {gate.get('metrics', {}).get('dangerous_caught', 'MISSING')}",
            f"- dangerous allowed: {gate.get('metrics', {}).get('dangerous_allowed', 'MISSING')}",
            f"- safe allow rate: {gate.get('metrics', {}).get('safe_allow_rate', 'MISSING')}",
            "",
            "## Noisy Policy-Pack Robustness",
        ]
    )
    for row in noisy.get("summaries", []):
        lines.append(
            f"- {row['condition']}: dangerous allowed={row['dangerous_allowed']}, safe allow rate={row['safe_allow_rate']:.2%}, causal@1={row['exact_causal_policy_identified_at_1']}"
        )
    lines.extend(["", "## Repair Baselines"])
    for row in repair.get("summaries", []):
        lines.append(
            f"- {row['method']}: naive after={row['naive_vbw_after_repair']}, critic after={row['critic_vbw_after_repair']}"
        )
    lines.extend(["", *_llm_table_lines(llm), "", "## External Issue Suite"])
    for case in external.get("cases", []):
        lines.append(
            f"- {case['case_id']}: before repair VBW={case['before_repair']['verified_but_wrong']}, gate={case['gate']['pre_selection_decision']}, after repair VBW={case['after_repair']['verified_but_wrong']}"
        )
    lines.extend(["", *_formal_table_lines(formal), "", *_external_vericoding_lines()])
    write_markdown(REPORTS_DIR / "evidence_pack.md", "\n".join(lines))

    table_lines = [
        "# Updated Paper Tables",
        "",
        "## Candidate-Set Underconstraint",
        "",
        "| Spec mode | Mean underconstraint risk | Tasks with existence risk | Selected VBW |",
        "|---|---:|---:|---:|",
    ]
    for row in under.get("aggregate", []):
        table_lines.append(
            f"| `{row['spec_mode']}` | {row['mean_underconstraint_risk']:.2f} | {row['tasks_with_existence_risk']}/{row['tasks']} | {row['selected_vbw_count']}/{row['tasks']} |"
        )
    table_lines.extend(["", "## LLM Policy-Split", ""])
    if llm.get("summaries"):
        table_lines.extend(
            [
                "| Condition | Valid specs | Causal policy omitted | Selected VBW | Gate caught dangerous | Repair cleared |",
                "|---|---:|---:|---:|---:|---:|",
            ]
        )
        for row in llm["summaries"]:
            table_lines.append(
                f"| `{row['condition']}` | {row['valid_specs']} | {row['causal_policy_omitted_count']} | {row['selected_vbw_count']} | {row['gate_caught_dangerous_count']} | {row['repair_cleared_count']} |"
            )
    else:
        table_lines.append("No quantitative LLM policy-split artifacts are currently cached.")
    table_lines.extend(["", "## Formal Demo", ""])
    if formal.get("checks"):
        table_lines.extend(
            [
                "| Check | Contract | Expected | Result |",
                "|---|---|---|---|",
            ]
        )
        for check in formal["checks"]:
            expected = "verifies" if check["expected_outcome"] == "pass" else "fails verification"
            actual = "PASS" if check["result"] == "PASS" else "FAIL"
            if check["expected_outcome"] == "fail" and check["actual_outcome"] == "fail":
                actual = "PASS, expected failure observed"
            table_lines.append(f"| {check['name']} | `{check['contract']}` | {expected} | {actual} |")
    else:
        table_lines.append(f"Formal demo status: `{formal.get('status', 'MISSING')}`.")
    write_markdown(REPORTS_DIR / "paper_updated_tables.md", "\n".join(table_lines))

    return {
        "result_type": "evidence_pack",
        "paths": [
            str(REPORTS_DIR / "evidence_pack.md"),
            str(REPORTS_DIR / "paper_updated_tables.md"),
            str(REPORTS_DIR / "paper_insert_llm_policy_split.md"),
            str(REPORTS_DIR / "paper_insert_formal_demo.md"),
        ],
    }


if __name__ == "__main__":
    build_evidence_pack()
