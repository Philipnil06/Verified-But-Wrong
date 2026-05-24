from __future__ import annotations

from typing import Any

from analysis.common import REPORTS_DIR, split_for_task, timestamp, write_json, write_markdown
from llm_selection import BASELINE_REQUIREMENTS, evaluate_candidates_with_requirement_tests, run_candidate_ranking_with_requirement_tests
from runner import evaluate_candidates, list_tasks, load_task, rank_candidates, run_task
from spec_audit_calibration import _mode_spec_text
from spec_audit_gate import audit_public_spec
from spec_repair import repair_spec_from_audit


CANDIDATE_SET_UNDERCONSTRAINT_JSON = REPORTS_DIR / "candidate_set_underconstraint.json"
CANDIDATE_SET_UNDERCONSTRAINT_MD = REPORTS_DIR / "candidate_set_underconstraint.md"


def _requirements_from_repaired_audit(task_id: str, audit_result: dict[str, Any]) -> list[str]:
    requirements = []
    baseline = BASELINE_REQUIREMENTS.get(task_id, {}).get("requirement")
    if baseline:
        requirements.append(baseline)
    for card in audit_result.get("covered_policy_cards", []):
        requirement_test = card.get("requirement_test")
        if requirement_test and requirement_test not in requirements:
            requirements.append(requirement_test)
    return requirements


def _public_passing_metrics(candidate_results: list[dict[str, Any]]) -> dict[str, Any]:
    public_passing = [candidate for candidate in candidate_results if candidate["public_passed"]]
    hidden_failing = [candidate for candidate in public_passing if not candidate["hidden_passed"]]
    hidden_passing = [candidate for candidate in public_passing if candidate["hidden_passed"]]
    count = len(public_passing)
    risk = len(hidden_failing) / count if count else 0.0
    return {
        "public_passing_candidates": [candidate["name"] for candidate in public_passing],
        "public_passing_hidden_failing_candidates": [candidate["name"] for candidate in hidden_failing],
        "public_passing_hidden_passing_candidates": [candidate["name"] for candidate in hidden_passing],
        "public_passing_candidates_count": count,
        "public_passing_hidden_failing_count": len(hidden_failing),
        "public_passing_hidden_passing_count": len(hidden_passing),
        "underconstraint_risk": risk,
        "existence_risk": bool(hidden_failing),
        "random_selection_vbw_probability": risk,
    }


def _evaluate_benchmark_mode(task: dict[str, Any], mode: str) -> dict[str, Any]:
    candidates = evaluate_candidates(task, mode)
    ranked = rank_candidates(candidates)
    selected = next(candidate for candidate in ranked if candidate["name"] == ranked[0]["name"])
    metrics = _public_passing_metrics(candidates)
    return {
        "task_id": task["id"],
        "task_title": task["title"],
        "split": split_for_task(task["id"]),
        "spec_mode": mode,
        "selected_candidate": selected["name"],
        "selected_vbw": bool(selected["public_passed"] and not selected["hidden_passed"]),
        **metrics,
    }


def _evaluate_repaired_mode(task: dict[str, Any], base_mode: str) -> dict[str, Any]:
    spec_text, spec_source = _mode_spec_text(task, base_mode)
    before = run_task(task["id"], base_mode)
    audit_before = audit_public_spec(
        task_id=task["id"],
        spec_text=spec_text,
        policy_pack_ids=task.get("policy_pack_ids"),
        mode=base_mode,
        selection_result=before,
        post_selection=True,
        spec_source=spec_source,
    )
    repaired = repair_spec_from_audit(spec_text, audit_before)
    audit_after = audit_public_spec(
        task_id=task["id"],
        spec_text=repaired["repaired_spec_text"],
        policy_pack_ids=task.get("policy_pack_ids"),
        mode=f"repaired_{base_mode}",
        post_selection=False,
        spec_source=f"repair:{spec_source}",
    )
    selected_requirements = _requirements_from_repaired_audit(task["id"], audit_after)
    evaluated = evaluate_candidates_with_requirement_tests(task["id"], selected_requirements)
    ranked = run_candidate_ranking_with_requirement_tests(task["id"], selected_requirements)
    metrics = _public_passing_metrics(evaluated["candidate_results"])
    return {
        "task_id": task["id"],
        "task_title": task["title"],
        "split": split_for_task(task["id"]),
        "spec_mode": f"repaired_{base_mode}",
        "selected_candidate": ranked["selected_candidate"],
        "selected_vbw": ranked["verified_but_wrong"],
        "selected_requirements": selected_requirements,
        **metrics,
    }


def _aggregate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    mode_order = ["naive", "critic", "oracle", "repaired_naive", "repaired_critic"]
    summaries = []
    for mode in mode_order:
        mode_rows = [row for row in rows if row["spec_mode"] == mode]
        if not mode_rows:
            continue
        total_public_passing = sum(row["public_passing_candidates_count"] for row in mode_rows)
        total_hidden_failing = sum(row["public_passing_hidden_failing_count"] for row in mode_rows)
        summaries.append(
            {
                "spec_mode": mode,
                "tasks": len(mode_rows),
                "public_passing_candidates": total_public_passing,
                "hidden_failing_among_public_passing": total_hidden_failing,
                "hidden_passing_among_public_passing": sum(
                    row["public_passing_hidden_passing_count"] for row in mode_rows
                ),
                "mean_underconstraint_risk": sum(row["underconstraint_risk"] for row in mode_rows) / len(mode_rows),
                "tasks_with_existence_risk": sum(1 for row in mode_rows if row["existence_risk"]),
                "selected_vbw_count": sum(1 for row in mode_rows if row["selected_vbw"]),
                "random_selection_vbw_probability_mean": sum(
                    row["random_selection_vbw_probability"] for row in mode_rows
                )
                / len(mode_rows),
            }
        )
    return summaries


def write_candidate_set_underconstraint_report(result: dict[str, Any]) -> None:
    lines = [
        "# Candidate-Set Underconstraint Analysis",
        "",
        "This analysis evaluates all candidate implementations for each task/spec-mode pair. Hidden oracles are used only for evaluation analysis, not for pre-selection gating.",
        "",
        "## Aggregate Candidate-Set Underconstraint",
        "",
        "| Spec mode | Public-passing candidates | Hidden-failing among public-passing | Mean underconstraint risk | Tasks with existence risk | Selected VBW |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in result["aggregate"]:
        lines.append(
            f"| `{row['spec_mode']}` | {row['public_passing_candidates']} | "
            f"{row['hidden_failing_among_public_passing']} | {row['mean_underconstraint_risk']:.2f} | "
            f"{row['tasks_with_existence_risk']}/{row['tasks']} | {row['selected_vbw_count']}/{row['tasks']} |"
        )

    lines.extend(
        [
            "",
            "## Per-Task Candidate-Set Underconstraint",
            "",
            "| Task | Split | Spec mode | Selected candidate | Public-passing | Hidden-failing among public-passing | Underconstraint risk | Existence risk | Selected VBW |",
            "|---|---|---|---|---:|---:|---:|---|---|",
        ]
    )
    for row in result["rows"]:
        lines.append(
            f"| `{row['task_id']}` | {row['split']} | `{row['spec_mode']}` | `{row['selected_candidate']}` | "
            f"{row['public_passing_candidates_count']} | {row['public_passing_hidden_failing_count']} | "
            f"{row['underconstraint_risk']:.2f} | {row['existence_risk']} | {row['selected_vbw']} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Incomplete specs do not merely select one bad candidate under a fixed ordering. They admit broader sets of bad-but-public-spec-passing candidates, which means the public spec underconstrains the implementation-selection target.",
        ]
    )
    write_markdown(CANDIDATE_SET_UNDERCONSTRAINT_MD, "\n".join(lines))


def run_candidate_set_underconstraint_analysis() -> dict[str, Any]:
    rows = []
    for task in list_tasks():
        rows.append(_evaluate_benchmark_mode(task, "naive"))
        rows.append(_evaluate_benchmark_mode(task, "critic"))
        rows.append(_evaluate_benchmark_mode(task, "oracle"))
        rows.append(_evaluate_repaired_mode(task, "naive"))
        rows.append(_evaluate_repaired_mode(task, "critic"))

    result = {
        "result_type": "candidate_set_underconstraint",
        "timestamp": timestamp(),
        "tasks": len(list_tasks()),
        "rows": rows,
        "aggregate": _aggregate(rows),
    }
    write_json(CANDIDATE_SET_UNDERCONSTRAINT_JSON, result)
    write_candidate_set_underconstraint_report(result)
    return result


if __name__ == "__main__":
    run_candidate_set_underconstraint_analysis()
