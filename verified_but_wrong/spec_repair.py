from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from llm_selection import BASELINE_REQUIREMENTS, run_candidate_ranking_with_requirement_tests
from runner import RESULTS_DIR, list_tasks, run_task
from spec_audit_calibration import _mode_spec_text
from spec_audit_gate import audit_public_spec


SPEC_REPAIR_LATEST_JSON = RESULTS_DIR / "spec_repair_latest.json"
SPEC_REPAIR_RUNS_JSONL = RESULTS_DIR / "spec_repair_runs.jsonl"
SPEC_REPAIR_REPORT = RESULTS_DIR / "spec_repair_report.md"
SPEC_REPAIR_BASELINES_LATEST_JSON = RESULTS_DIR / "spec_repair_baselines_latest.json"
SPEC_REPAIR_BASELINES_REPORT = RESULTS_DIR / "spec_repair_baselines_report.md"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _append_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def repair_spec_from_audit(spec_text: str, audit_result: dict[str, Any]) -> dict[str, Any]:
    patch_cards = audit_result.get("missing_policy_cards", []) + audit_result.get("unclear_policy_cards", [])
    patches = []
    patched_ids = []
    repaired = spec_text.strip()
    for card in patch_cards:
        patch = card.get("suggested_spec_patch")
        card_id = card.get("policy_card_id")
        if not patch or patch in repaired:
            continue
        patches.append(patch)
        patched_ids.append(card_id)
    if patches:
        repaired += "\n\nPolicy audit additions:\n" + "\n".join(f"- {patch}" for patch in patches)
    return {
        "original_spec_text": spec_text,
        "repaired_spec_text": repaired,
        "patched_policy_card_ids": patched_ids,
        "patches": patches,
        "repair_notes": [
            "Deterministic repair appends suggested policy-card patches.",
            "No generated code or LLM output is executed.",
        ],
    }


def _requirements_from_audit(task_id: str, audit_result: dict[str, Any]) -> list[str]:
    requirements = []
    baseline = BASELINE_REQUIREMENTS.get(task_id, {}).get("requirement")
    if baseline:
        requirements.append(baseline)
    for card in audit_result.get("covered_policy_cards", []):
        requirement_test = card.get("requirement_test")
        if requirement_test and requirement_test not in requirements:
            requirements.append(requirement_test)
    return requirements


def _run_one(task: dict[str, Any], mode: str) -> dict[str, Any]:
    spec_text, spec_source = _mode_spec_text(task, mode)
    before = run_task(task["id"], mode)
    audit_before = audit_public_spec(
        task_id=task["id"],
        spec_text=spec_text,
        policy_pack_ids=task.get("policy_pack_ids"),
        mode=mode,
        selection_result=before,
        post_selection=True,
        spec_source=spec_source,
    )
    repair = repair_spec_from_audit(spec_text, audit_before)
    audit_after = audit_public_spec(
        task_id=task["id"],
        spec_text=repair["repaired_spec_text"],
        policy_pack_ids=task.get("policy_pack_ids"),
        mode="repaired",
        selection_result=None,
        post_selection=False,
        spec_source=f"repair:{spec_source}",
    )
    selected_requirements = _requirements_from_audit(task["id"], audit_after)
    ranking_after = run_candidate_ranking_with_requirement_tests(task["id"], selected_requirements)
    return {
        "timestamp": _timestamp(),
        "task_id": task["id"],
        "task_title": task["title"],
        "mode": mode,
        "verified_but_wrong_before": before["verified_but_wrong"],
        "selected_candidate_before": before["selected_candidate"],
        "pre_selection_decision_before": audit_before["pre_selection_decision"],
        "repair": repair,
        "selected_requirements_after_repair": selected_requirements,
        "pre_selection_decision_after": audit_after["pre_selection_decision"],
        "verified_but_wrong_after": ranking_after["verified_but_wrong"],
        "selected_candidate_after": ranking_after["selected_candidate"],
        "hidden_oracle_passed_after": ranking_after["hidden_oracle_passed"],
        "audit_before": audit_before,
        "audit_after": audit_after,
        "ranking_after": ranking_after,
    }


def _summary(rows: list[dict[str, Any]], mode: str) -> dict[str, Any]:
    mode_rows = [row for row in rows if row["mode"] == mode]
    patches = [len(row["repair"]["patches"]) for row in mode_rows]
    return {
        "mode": mode,
        "specs": len(mode_rows),
        "vbw_before_repair": sum(1 for row in mode_rows if row["verified_but_wrong_before"]),
        "vbw_after_repair": sum(1 for row in mode_rows if row["verified_but_wrong_after"]),
        "avg_patches_per_spec": sum(patches) / len(patches) if patches else 0.0,
        "remaining_failures": sum(1 for row in mode_rows if row["verified_but_wrong_after"]),
    }


def run_repair_experiment() -> dict[str, Any]:
    rows = []
    for task in list_tasks():
        for mode in ["naive", "critic"]:
            rows.append(_run_one(task, mode))
    result = {
        "result_type": "spec_repair_experiment",
        "timestamp": _timestamp(),
        "summaries": [_summary(rows, "naive"), _summary(rows, "critic")],
        "runs": rows,
    }
    _write_json(SPEC_REPAIR_LATEST_JSON, result)
    _append_jsonl(SPEC_REPAIR_RUNS_JSONL, rows)
    write_spec_repair_report(result)
    return result


def load_spec_repair_experiment() -> dict[str, Any] | None:
    if not SPEC_REPAIR_LATEST_JSON.exists():
        return None
    return json.loads(SPEC_REPAIR_LATEST_JSON.read_text(encoding="utf-8"))


def write_spec_repair_report(result: dict[str, Any]) -> None:
    lines = [
        "# Spec Repair Report",
        "",
        "Detection alone is not enough. This deterministic repair loop appends policy-card patches and reruns candidate selection using curated requirement tests.",
        "",
        "| Spec class | VBW before repair | VBW after repair | Avg patches/spec | Remaining failures |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in result.get("summaries", []):
        lines.append(
            f"| `{row['mode']}` | {row['vbw_before_repair']} | {row['vbw_after_repair']} | "
            f"{row['avg_patches_per_spec']:.2f} | {row['remaining_failures']} |"
        )

    for task_id, mode in [("loyalty_refund_reversal", "naive"), ("loyalty_refund_reversal", "critic")]:
        example = next((row for row in result["runs"] if row["task_id"] == task_id and row["mode"] == mode), None)
        lines.extend(["", f"## Example: {task_id} / {mode}", ""])
        if example:
            lines.extend(
                [
                    f"- before: `{example['selected_candidate_before']}`, VBW=`{example['verified_but_wrong_before']}`",
                    f"- after: `{example['selected_candidate_after']}`, VBW=`{example['verified_but_wrong_after']}`",
                    "- patches:",
                ]
            )
            for patch in example["repair"]["patches"]:
                lines.append(f"  - {patch}")
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- Repair is deterministic text patching, not semantic synthesis.",
            "- Repaired selection uses manually curated requirement-test mappings.",
            "- Generated patch text is never executed as code.",
        ]
    )
    SPEC_REPAIR_REPORT.write_text("\n".join(lines), encoding="utf-8")


def _repair_text(method: str, spec_text: str, audit: dict[str, Any], task: dict[str, Any], mode: str) -> tuple[str, list[str]]:
    if method == "no_repair":
        return spec_text, []
    if method == "generic_repair":
        patch = "Handle edge cases, invalid inputs, authorization, state updates, and business rules carefully."
        return spec_text + "\n\n" + patch, [patch]
    if method == "checklist_repair":
        patch = (
            "Check authorization, invalid inputs, boundary conditions, temporal rules, state updates, "
            "conservation constraints, and organization-specific business rules."
        )
        return spec_text + "\n\n" + patch, [patch]
    if method == "oracle_repair":
        oracle_text = task.get("full_oracle_spec") or task.get("critic_improved_spec") or spec_text
        return oracle_text, [oracle_text]
    repaired = repair_spec_from_audit(spec_text, audit)
    return repaired["repaired_spec_text"], repaired["patches"]


def run_repair_baselines() -> dict[str, Any]:
    methods = ["no_repair", "generic_repair", "checklist_repair", "policy_targeted_repair", "oracle_repair"]
    rows = []
    for task in list_tasks():
        for mode in ["naive", "critic"]:
            spec_text, spec_source = _mode_spec_text(task, mode)
            original = run_task(task["id"], mode)
            original_audit = audit_public_spec(task["id"], spec_text, task.get("policy_pack_ids"), mode=mode, selection_result=original, post_selection=True, spec_source=spec_source)
            for method in methods:
                repaired_text, patches = _repair_text(method, spec_text, original_audit, task, mode)
                if method == "no_repair":
                    vbw_after = original["verified_but_wrong"]
                    selected = original["selected_candidate"]
                elif method == "oracle_repair":
                    oracle = run_task(task["id"], "oracle")
                    vbw_after = oracle["verified_but_wrong"]
                    selected = oracle["selected_candidate"]
                else:
                    audit_after = audit_public_spec(task["id"], repaired_text, task.get("policy_pack_ids"), mode="repaired", spec_source=f"{method}:{spec_source}")
                    reqs = _requirements_from_audit(task["id"], audit_after)
                    ranking = run_candidate_ranking_with_requirement_tests(task["id"], reqs)
                    vbw_after = ranking["verified_but_wrong"]
                    selected = ranking["selected_candidate"]
                rows.append({"task_id": task["id"], "mode": mode, "method": method, "vbw_before": original["verified_but_wrong"], "vbw_after": vbw_after, "selected_after": selected, "patch_count": len(patches)})
    summaries = []
    for method in methods:
        method_rows = [row for row in rows if row["method"] == method]
        summaries.append(
            {
                "method": method,
                "naive_vbw_after_repair": sum(1 for row in method_rows if row["mode"] == "naive" and row["vbw_after"]),
                "critic_vbw_after_repair": sum(1 for row in method_rows if row["mode"] == "critic" and row["vbw_after"]),
                "avg_patches_per_spec": sum(row["patch_count"] for row in method_rows) / len(method_rows) if method_rows else 0.0,
                "notes": "upper bound" if method == "oracle_repair" else "deterministic baseline",
            }
        )
    result = {"result_type": "spec_repair_baselines", "timestamp": _timestamp(), "summaries": summaries, "runs": rows}
    _write_json(SPEC_REPAIR_BASELINES_LATEST_JSON, result)
    write_spec_repair_baselines_report(result)
    return result


def write_spec_repair_baselines_report(result: dict[str, Any]) -> None:
    lines = [
        "# Spec Repair Baselines Report",
        "",
        "| Repair method | Naive VBW after repair | Critic VBW after repair | Avg patches/spec | Notes |",
        "|---|---:|---:|---:|---|",
    ]
    for row in result["summaries"]:
        lines.append(
            f"| `{row['method']}` | {row['naive_vbw_after_repair']} | {row['critic_vbw_after_repair']} | "
            f"{row['avg_patches_per_spec']:.2f} | {row['notes']} |"
        )
    loyalty = [row for row in result["runs"] if row["task_id"] == "loyalty_refund_reversal" and row["mode"] == "critic"]
    lines.extend(["", "## Loyalty Case Study", "", "| Stage | VBW after | Selected |", "|---|---:|---|"])
    for row in loyalty:
        lines.append(f"| `{row['method']}` | {row['vbw_after']} | `{row['selected_after']}` |")
    SPEC_REPAIR_BASELINES_REPORT.write_text("\n".join(lines), encoding="utf-8")
