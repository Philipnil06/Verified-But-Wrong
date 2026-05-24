from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runner import RESULTS_DIR, list_tasks, run_task
from spec_audit_calibration import _mode_spec_text, _policy_gate_metrics, run_policy_gate_calibration
from spec_audit_gate import audit_public_spec
from spec_repair import run_repair_experiment


DEFENSE_BASELINES_LATEST_JSON = RESULTS_DIR / "defense_baselines_latest.json"
DEFENSE_BASELINES_REPORT = RESULTS_DIR / "defense_baselines_report.md"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _rows_for_decision(decision_fn) -> list[dict[str, Any]]:
    rows = []
    for task in list_tasks():
        for mode in ["naive", "critic", "oracle"]:
            selection = run_task(task["id"], mode)
            spec_text, source = _mode_spec_text(task, mode)
            decision = decision_fn(task, mode, spec_text, selection)
            rows.append(
                {
                    "task_id": task["id"],
                    "mode": mode,
                    "verified_but_wrong": selection["verified_but_wrong"],
                    "hidden_oracle_passed": selection["hidden_oracle_passed"],
                    "pre_selection_decision": decision,
                    "spec_source": source,
                }
            )
    return rows


def _summary(name: str, rows: list[dict[str, Any]], needs_hidden_oracle: bool, pre_selection: bool, notes: str) -> dict[str, Any]:
    metrics = _policy_gate_metrics(rows)
    return {
        "defense": name,
        "dangerous_caught": metrics["dangerous_caught"],
        "dangerous_allowed": metrics["dangerous_allowed"],
        "safe_allowed": metrics["safe_allowed"],
        "safe_reviewed": metrics["safe_reviewed"],
        "safe_blocked": metrics["safe_blocked"],
        "safe_allow_rate": metrics["safe_allow_rate"],
        "review_burden": metrics["review_burden_count"],
        "needs_hidden_oracle": needs_hidden_oracle,
        "pre_selection_deployable": pre_selection,
        "notes": notes,
    }


def run_defense_baselines() -> dict[str, Any]:
    no_audit = _rows_for_decision(lambda task, mode, spec, selection: "ALLOW")

    generic = _rows_for_decision(
        lambda task, mode, spec, selection: audit_public_spec(
            task["id"],
            spec,
            policy_pack_ids=["generic_critical_requirements"],
            mode=mode,
            selection_result=None,
            post_selection=False,
            spec_source="generic_baseline",
        )["pre_selection_decision"]
    )
    keyword_only = _rows_for_decision(
        lambda task, mode, spec, selection: "REVIEW"
        if any(word in spec.lower() for word in ["must", "only", "never", "invalid", "missing"])
        else "ALLOW"
    )

    critic_only = []
    for task in list_tasks():
        selection = run_task(task["id"], "critic")
        critic_only.append(
            {
                "task_id": task["id"],
                "mode": "critic",
                "verified_but_wrong": selection["verified_but_wrong"],
                "hidden_oracle_passed": selection["hidden_oracle_passed"],
                "pre_selection_decision": "BLOCK" if selection["verified_but_wrong"] else "ALLOW",
            }
        )

    policy = run_policy_gate_calibration()["runs"]
    policy_no_severity = _rows_for_decision(
        lambda task, mode, spec, selection: "REVIEW"
        if audit_public_spec(task["id"], spec, policy_pack_ids=task.get("policy_pack_ids"), mode=mode)["missing_policy_cards"]
        or audit_public_spec(task["id"], spec, policy_pack_ids=task.get("policy_pack_ids"), mode=mode)["unclear_policy_cards"]
        else "ALLOW"
    )

    repair = run_repair_experiment()
    repair_rows = []
    for row in repair["runs"]:
        repair_rows.append(
            {
                "task_id": row["task_id"],
                "mode": row["mode"],
                "verified_but_wrong": row["verified_but_wrong_after"],
                "hidden_oracle_passed": row["hidden_oracle_passed_after"],
                "pre_selection_decision": "BLOCK" if row["verified_but_wrong_after"] else "ALLOW",
            }
        )

    hidden_oracle = _rows_for_decision(
        lambda task, mode, spec, selection: "BLOCK" if selection["verified_but_wrong"] else "ALLOW"
    )

    baselines = [
        _summary("No audit", no_audit, False, True, "Always allows every spec."),
        _summary("Keyword-only gate", keyword_only, False, True, "Uses raw spec keywords without policy structure."),
        _summary("Generic checklist audit", generic, False, True, "Uses only generic policy cards."),
        _summary("Checklist critic only", critic_only, True, False, "Uses critic-mode downstream outcome as a defense proxy."),
        _summary("Policy coverage gate", policy_no_severity, False, True, "Uses task-specific cards but no severity/category weighting."),
        _summary("Policy Audit Gate", policy, False, True, "Uses task policy packs before selection."),
        _summary("Policy Audit Gate + repair", repair_rows, False, True, "Runs policy-targeted deterministic repair after audit."),
        _summary("Hidden Oracle post-selection", hidden_oracle, True, False, "Catches failures after selection; not a pre-selection spec audit."),
    ]

    result = {"result_type": "defense_baselines", "timestamp": _timestamp(), "baselines": baselines}
    _write_json(DEFENSE_BASELINES_LATEST_JSON, result)
    write_defense_baselines_report(result)
    return result


def write_defense_baselines_report(result: dict[str, Any]) -> None:
    lines = [
        "# Defense Baselines Report",
        "",
        "| Defense | Dangerous caught | Dangerous allowed | Safe allowed | Safe blocked | Review burden | Needs hidden oracle | Pre-selection deployable |",
        "|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in result["baselines"]:
        lines.append(
            f"| {row['defense']} | {row['dangerous_caught']} | {row['dangerous_allowed']} | "
            f"{row['safe_allowed']} | {row['safe_blocked']} | {row['review_burden']} | "
            f"{row['needs_hidden_oracle']} | {row['pre_selection_deployable']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The policy audit gate is compared against no audit, generic policy checks, critic-only selection, and hidden-oracle post-selection. Hidden oracles can catch failures after selection, but they are not a pre-selection deployment gate.",
        ]
    )
    DEFENSE_BASELINES_REPORT.write_text("\n".join(lines), encoding="utf-8")
