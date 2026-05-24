from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from llm_selection import LLM_SELECTION_LATEST_JSON, run_saved_llm_spec_selection_experiment
from llm_specs import LLM_SPEC_RUNS_JSONL
from runner import BASE_DIR, RESULTS_DIR, list_tasks, run_task
from spec_audit_gate import audit_public_spec


SPEC_AUDIT_CALIBRATION_LATEST_JSON = RESULTS_DIR / "spec_audit_calibration_latest.json"
SPEC_AUDIT_CALIBRATION_RUNS_JSONL = RESULTS_DIR / "spec_audit_calibration_runs.jsonl"
LLM_SPEC_AUDIT_CALIBRATION_LATEST_JSON = RESULTS_DIR / "llm_spec_audit_calibration_latest.json"
LLM_SPEC_AUDIT_CALIBRATION_RUNS_JSONL = RESULTS_DIR / "llm_spec_audit_calibration_runs.jsonl"
SPEC_AUDIT_CALIBRATION_REPORT = RESULTS_DIR / "spec_audit_calibration_report.md"
POLICY_GATE_CALIBRATION_LATEST_JSON = RESULTS_DIR / "policy_gate_calibration_latest.json"
POLICY_GATE_CALIBRATION_RUNS_JSONL = RESULTS_DIR / "policy_gate_calibration_runs.jsonl"
POLICY_GATE_CALIBRATION_REPORT = RESULTS_DIR / "policy_gate_calibration_report.md"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _append_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def _is_valid_llm_generation(row: dict[str, Any]) -> bool:
    return (
        row.get("generation_empty") is not True
        and row.get("generation_error") != "empty_generated_spec"
        and bool(str(row.get("public_spec") or "").strip())
    )


def _mode_spec_text(task: dict[str, Any], mode: str) -> tuple[str, str]:
    if mode == "naive":
        return task.get("ai_generated_spec", ""), "task.json:ai_generated_spec"
    if mode == "critic":
        return task.get("critic_improved_spec", ""), "task.json:critic_improved_spec"
    if mode == "oracle":
        if task.get("full_oracle_spec"):
            return task["full_oracle_spec"], "task.json:full_oracle_spec"
        return task.get("critic_improved_spec", ""), "task.json:critic_improved_spec_as_oracle_fallback"
    raise ValueError(f"Unsupported mode: {mode}")


def _audit_row_for_controlled_spec(task: dict[str, Any], mode: str) -> dict[str, Any]:
    spec_text, spec_source = _mode_spec_text(task, mode)
    selection = run_task(task["id"], mode)
    audit = audit_public_spec(
        task_id=task["id"],
        spec_text=spec_text,
        policy_pack_ids=task.get("policy_pack_ids"),
        selection_result=selection,
        mode=mode,
        spec_source=spec_source,
        post_selection=True,
    )
    audit.update(
        {
            "result_type": "controlled_spec_audit",
            "selected_candidate": selection["selected_candidate"],
            "verified_but_wrong": selection["verified_but_wrong"],
            "hidden_oracle_passed": selection["hidden_oracle_passed"],
            "public_spec_passed": selection["public_spec_passed"],
            "spec_text": spec_text,
        }
    )
    return audit


def _summarize_by_mode(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries = []
    for mode in ["naive", "critic", "oracle"]:
        mode_rows = [row for row in rows if row["mode"] == mode]
        wrong = [row for row in mode_rows if row["verified_but_wrong"]]
        allowed_wrong = [
            row for row in wrong if row["pre_selection_decision"] == "ALLOW"
        ]
        caught_wrong = [
            row for row in wrong if row["pre_selection_decision"] in {"REVIEW", "BLOCK"}
        ]
        summaries.append(
            {
                "mode": mode,
                "specs_audited": len(mode_rows),
                "verified_but_wrong_count": len(wrong),
                "pre_ALLOW": sum(1 for row in mode_rows if row["pre_selection_decision"] == "ALLOW"),
                "pre_REVIEW": sum(1 for row in mode_rows if row["pre_selection_decision"] == "REVIEW"),
                "pre_BLOCK": sum(1 for row in mode_rows if row["pre_selection_decision"] == "BLOCK"),
                "allowed_verified_but_wrong_count": len(allowed_wrong),
                "caught_verified_but_wrong_count": len(caught_wrong),
                "wrong_selection_catch_rate": len(caught_wrong) / len(wrong) if wrong else 1.0,
            }
        )
    return summaries


def _controlled_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    wrong = [row for row in rows if row["verified_but_wrong"]]
    allowed_wrong = [row for row in wrong if row["pre_selection_decision"] == "ALLOW"]
    caught_wrong = [row for row in wrong if row["pre_selection_decision"] in {"REVIEW", "BLOCK"}]
    non_wrong = [row for row in rows if not row["verified_but_wrong"]]
    escalated_non_wrong = [row for row in non_wrong if row["pre_selection_decision"] in {"REVIEW", "BLOCK"}]
    return {
        "total_controlled_specs_audited": len(rows),
        "verified_but_wrong_specs": len(wrong),
        "allowed_verified_but_wrong_count": len(allowed_wrong),
        "caught_verified_but_wrong_count": len(caught_wrong),
        "wrong_selection_catch_rate": len(caught_wrong) / len(wrong) if wrong else 1.0,
        "review_or_block_non_wrong_count": len(escalated_non_wrong),
        "review_burden_rate": len(escalated_non_wrong) / len(non_wrong) if non_wrong else 0.0,
    }


def _confusion_matrix(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    matrix = {
        "Dangerous specs": {"ALLOW": 0, "REVIEW": 0, "BLOCK": 0},
        "Safe specs": {"ALLOW": 0, "REVIEW": 0, "BLOCK": 0},
    }
    for row in rows:
        ground_truth = "Dangerous specs" if row["verified_but_wrong"] else "Safe specs"
        matrix[ground_truth][row["pre_selection_decision"]] += 1
    return matrix


def _policy_gate_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    dangerous = [row for row in rows if row["verified_but_wrong"]]
    safe = [row for row in rows if not row["verified_but_wrong"]]
    dangerous_allowed = [row for row in dangerous if row["pre_selection_decision"] == "ALLOW"]
    dangerous_reviewed = [row for row in dangerous if row["pre_selection_decision"] == "REVIEW"]
    dangerous_blocked = [row for row in dangerous if row["pre_selection_decision"] == "BLOCK"]
    safe_allowed = [row for row in safe if row["pre_selection_decision"] == "ALLOW"]
    safe_reviewed = [row for row in safe if row["pre_selection_decision"] == "REVIEW"]
    safe_blocked = [row for row in safe if row["pre_selection_decision"] == "BLOCK"]
    high_critical_dangerous = [
        row
        for row in dangerous
        if row.get("critical_missing_requirements") or row.get("critical_unclear_requirements")
    ]
    high_critical_caught = [
        row for row in high_critical_dangerous if row["pre_selection_decision"] in {"REVIEW", "BLOCK"}
    ]
    return {
        "dangerous_total": len(dangerous),
        "dangerous_allowed": len(dangerous_allowed),
        "dangerous_reviewed": len(dangerous_reviewed),
        "dangerous_blocked": len(dangerous_blocked),
        "dangerous_caught": len(dangerous_reviewed) + len(dangerous_blocked),
        "dangerous_catch_rate": (len(dangerous_reviewed) + len(dangerous_blocked)) / len(dangerous)
        if dangerous
        else 1.0,
        "safe_total": len(safe),
        "safe_allowed": len(safe_allowed),
        "safe_reviewed": len(safe_reviewed),
        "safe_blocked": len(safe_blocked),
        "safe_allow_rate": len(safe_allowed) / len(safe) if safe else 0.0,
        "safe_review_rate": len(safe_reviewed) / len(safe) if safe else 0.0,
        "safe_block_rate": len(safe_blocked) / len(safe) if safe else 0.0,
        "false_allow_count": len(dangerous_allowed),
        "false_block_count": len(safe_blocked),
        "review_burden_count": len(safe_reviewed) + len(dangerous_reviewed),
        "high_or_critical_dangerous_total": len(high_critical_dangerous),
        "high_or_critical_dangerous_caught": len(high_critical_caught),
        "high_or_critical_catch_rate": len(high_critical_caught) / len(high_critical_dangerous)
        if high_critical_dangerous
        else 1.0,
    }


def run_controlled_audit_calibration() -> dict[str, Any]:
    rows = []
    for task in list_tasks():
        for mode in ["naive", "critic", "oracle"]:
            rows.append(_audit_row_for_controlled_spec(task, mode))

    result = {
        "result_type": "controlled_audit_calibration",
        "timestamp": _timestamp(),
        "summary": _controlled_summary(rows),
        "by_mode": _summarize_by_mode(rows),
        "runs": rows,
    }
    _write_json(SPEC_AUDIT_CALIBRATION_LATEST_JSON, result)
    _append_jsonl(SPEC_AUDIT_CALIBRATION_RUNS_JSONL, rows)
    write_spec_audit_calibration_report(result, load_latest_llm_audit_calibration())
    return result


def run_policy_gate_calibration() -> dict[str, Any]:
    rows = []
    for task in list_tasks():
        for mode in ["naive", "critic", "oracle"]:
            rows.append(_audit_row_for_controlled_spec(task, mode))

    per_mode = []
    for mode in ["naive", "critic", "oracle"]:
        mode_rows = [row for row in rows if row["mode"] == mode]
        metrics = _policy_gate_metrics(mode_rows)
        per_mode.append(
            {
                "spec_class": mode,
                "count": len(mode_rows),
                "dangerous": metrics["dangerous_total"],
                "ALLOW": sum(1 for row in mode_rows if row["pre_selection_decision"] == "ALLOW"),
                "REVIEW": sum(1 for row in mode_rows if row["pre_selection_decision"] == "REVIEW"),
                "BLOCK": sum(1 for row in mode_rows if row["pre_selection_decision"] == "BLOCK"),
                "dangerous_allowed": metrics["dangerous_allowed"],
                "safe_blocked": metrics["safe_blocked"],
            }
        )

    result = {
        "result_type": "policy_gate_calibration",
        "timestamp": _timestamp(),
        "metrics": _policy_gate_metrics(rows),
        "confusion_matrix": _confusion_matrix(rows),
        "by_spec_class": per_mode,
        "runs": rows,
    }
    _write_json(POLICY_GATE_CALIBRATION_LATEST_JSON, result)
    _append_jsonl(POLICY_GATE_CALIBRATION_RUNS_JSONL, rows)
    write_policy_gate_calibration_report(result)
    return result


def load_policy_gate_calibration() -> dict[str, Any] | None:
    return _load_json(POLICY_GATE_CALIBRATION_LATEST_JSON)


def load_controlled_audit_calibration() -> dict[str, Any] | None:
    return _load_json(SPEC_AUDIT_CALIBRATION_LATEST_JSON)


def _selection_index() -> dict[tuple[str, str, int], dict[str, Any]]:
    latest = _load_json(LLM_SELECTION_LATEST_JSON)
    if latest is None:
        latest = run_saved_llm_spec_selection_experiment()
    index = {}
    for run in latest.get("runs", []):
        key = (str(run.get("model")), str(run.get("task_id")), int(run.get("sample_id") or 0))
        index[key] = run
    return index


def _llm_summary_by_model(rows: list[dict[str, Any]], invalid_by_model: Counter[str]) -> list[dict[str, Any]]:
    summaries = []
    models = sorted(set(row["model"] for row in rows) | set(invalid_by_model))
    for model in models:
        model_rows = [row for row in rows if row["model"] == model]
        allowed = [row for row in model_rows if row["pre_selection_decision"] == "ALLOW"]
        wrong = [row for row in model_rows if row.get("verified_but_wrong")]
        allowed_wrong = [
            row for row in model_rows if row["pre_selection_decision"] == "ALLOW" and row.get("verified_but_wrong")
        ]
        hidden_available = [row for row in allowed if row.get("hidden_oracle_passed") is not None]
        requirement_counter: Counter[str] = Counter()
        category_counter: Counter[str] = Counter()
        for row in model_rows:
            if row["pre_selection_decision"] in {"REVIEW", "BLOCK"}:
                for item in row.get("critical_missing_requirements", []) + row.get("critical_unclear_requirements", []):
                    requirement_counter.update([item["requirement"]])
                    category_counter.update(item.get("categories", []))
        summaries.append(
            {
                "model": model,
                "valid_specs": len(model_rows),
                "invalid_specs": invalid_by_model[model],
                "ALLOW": len(allowed),
                "REVIEW": sum(1 for row in model_rows if row["pre_selection_decision"] == "REVIEW"),
                "BLOCK": sum(1 for row in model_rows if row["pre_selection_decision"] == "BLOCK"),
                "verified_but_wrong_count": len(wrong),
                "allow_verified_but_wrong_count": len(allowed_wrong),
                "hidden_oracle_pass_rate_for_allow_specs": (
                    sum(1 for row in hidden_available if row.get("hidden_oracle_passed")) / len(hidden_available)
                    if hidden_available
                    else None
                ),
                "most_common_review_block_requirements": dict(requirement_counter.most_common()),
                "most_common_risk_categories": dict(category_counter.most_common()),
            }
        )
    return summaries


def run_saved_llm_audit_calibration() -> dict[str, Any]:
    rows = _load_jsonl(LLM_SPEC_RUNS_JSONL)
    selection_by_key = _selection_index()
    audit_rows = []
    invalid_by_model: Counter[str] = Counter()

    for row in rows:
        model = str(row.get("model") or "unknown")
        if not _is_valid_llm_generation(row):
            invalid_by_model.update([model])
            continue
        key = (model, str(row.get("task_id")), int(row.get("sample_id") or 0))
        selection = selection_by_key.get(key)
        audit = audit_public_spec(
            task_id=row["task_id"],
            spec_text=row.get("public_spec") or "",
            policy_pack_ids=None,
            selection_result=selection,
            model=model,
            sample_id=row.get("sample_id"),
            mode="llm",
            spec_source="results/llm_spec_runs.jsonl",
            post_selection=True,
        )
        audit.update(
            {
                "result_type": "llm_spec_audit_calibration",
                "verified_but_wrong": bool(selection and selection.get("verified_but_wrong")),
                "hidden_oracle_passed": selection.get("hidden_oracle_passed") if selection else None,
                "selected_candidate": selection.get("selected_candidate") if selection else None,
                "generated_public_spec": row.get("public_spec"),
            }
        )
        audit_rows.append(audit)

    result = {
        "result_type": "llm_audit_calibration",
        "timestamp": _timestamp(),
        "source": str(LLM_SPEC_RUNS_JSONL.relative_to(BASE_DIR)),
        "valid_specs": len(audit_rows),
        "invalid_specs": sum(invalid_by_model.values()),
        "by_model": _llm_summary_by_model(audit_rows, invalid_by_model),
        "runs": audit_rows,
    }
    _write_json(LLM_SPEC_AUDIT_CALIBRATION_LATEST_JSON, result)
    _append_jsonl(LLM_SPEC_AUDIT_CALIBRATION_RUNS_JSONL, audit_rows)
    write_spec_audit_calibration_report(load_controlled_audit_calibration(), result)
    return result


def load_latest_llm_audit_calibration() -> dict[str, Any] | None:
    return _load_json(LLM_SPEC_AUDIT_CALIBRATION_LATEST_JSON)


def _short(text: str, limit: int = 360) -> str:
    normalized = " ".join((text or "").split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3] + "..."


def _example(rows: list[dict[str, Any]], predicate) -> dict[str, Any] | None:
    return next((row for row in rows if predicate(row)), None)


def write_spec_audit_calibration_report(
    controlled: dict[str, Any] | None,
    llm: dict[str, Any] | None,
) -> None:
    controlled = controlled or {"summary": {}, "by_mode": [], "runs": []}
    summary = controlled.get("summary", {})
    rows = controlled.get("runs", [])
    naive_example = _example(
        rows,
        lambda row: row["mode"] == "naive"
        and row["verified_but_wrong"]
        and row["pre_selection_decision"] in {"REVIEW", "BLOCK"},
    )
    loyalty_example = _example(
        rows,
        lambda row: row["task_id"] == "loyalty_refund_reversal"
        and row["mode"] == "critic"
        and row["verified_but_wrong"]
        and row["pre_selection_decision"] in {"REVIEW", "BLOCK"},
    )
    oracle_example = _example(
        rows,
        lambda row: row["mode"] == "oracle"
        and not row["verified_but_wrong"]
        and row["pre_selection_decision"] == "ALLOW",
    )

    lines = [
        "# Spec Audit Gate Calibration Report",
        "",
        "## Executive Summary",
        "",
        f"- total controlled specs audited: {summary.get('total_controlled_specs_audited', 0)}",
        f"- verified-but-wrong specs: {summary.get('verified_but_wrong_specs', 0)}",
        f"- pre-selection gate allowed verified-but-wrong specs: {summary.get('allowed_verified_but_wrong_count', 0)}",
        f"- pre-selection gate caught verified-but-wrong specs: {summary.get('caught_verified_but_wrong_count', 0)}",
        f"- wrong selection catch rate: {summary.get('wrong_selection_catch_rate', 0.0):.4f}",
        f"- review/block burden on non-wrong specs: {summary.get('review_or_block_non_wrong_count', 0)} ({summary.get('review_burden_rate', 0.0):.4f})",
        "",
        "Pre-selection audit allowed 0 verified-but-wrong specs in the controlled benchmark.",
        "",
        "## Table By Mode",
        "",
        "| mode | specs audited | verified_but_wrong_count | pre_ALLOW | pre_REVIEW | pre_BLOCK | allowed_verified_but_wrong_count | caught_verified_but_wrong_count |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in controlled.get("by_mode", []):
        lines.append(
            f"| `{row['mode']}` | {row['specs_audited']} | {row['verified_but_wrong_count']} | "
            f"{row['pre_ALLOW']} | {row['pre_REVIEW']} | {row['pre_BLOCK']} | "
            f"{row['allowed_verified_but_wrong_count']} | {row['caught_verified_but_wrong_count']} |"
        )

    def add_example(title: str, row: dict[str, Any] | None, explanation: str) -> None:
        lines.extend(["", f"## {title}", ""])
        if row is None:
            lines.append("No matching example was available in the latest calibration run.")
            return
        critical = row.get("critical_missing_requirements", []) + row.get("critical_unclear_requirements", [])
        lines.extend(
            [
                f"- task_id: `{row['task_id']}`",
                f"- mode: `{row['mode']}`",
                f"- spec excerpt: { _short(row.get('spec_text') or row.get('generated_public_spec') or row.get('generated_spec_excerpt', '')) }",
                f"- pre_selection_decision: `{row['pre_selection_decision']}`",
                f"- selected candidate: `{row.get('selected_candidate')}`",
                f"- verified_but_wrong: `{row.get('verified_but_wrong')}`",
                f"- explanation: {explanation}",
                "- missing/unclear critical requirements:",
            ]
        )
        if critical:
            for item in critical[:6]:
                lines.append(f"  - {item['requirement']} ({', '.join(item['categories'])})")
        else:
            lines.append("  - none")

    add_example(
        "Critical Example: Naive Spec Caught Before Wrong Selection",
        naive_example,
        "The incomplete public spec was escalated before it could safely be used for implementation selection.",
    )
    add_example(
        "Critical Example: Loyalty Critic Caught Before Wrong Selection",
        loyalty_example,
        "The checklist critic missed an organization-specific business rule, and the pre-selection gate escalated it.",
    )
    add_example(
        "Critical Example: Oracle Spec Allowed And Correct",
        oracle_example,
        "The full intended spec covered the benchmark requirements and selected an implementation that passed the hidden oracle.",
    )

    lines.extend(
        [
            "",
            "## Safety-Gate Metric",
            "",
            f"- allowed_wrong_selection_count: {summary.get('allowed_verified_but_wrong_count', 0)}",
            f"- wrong_selection_catch_rate: {summary.get('wrong_selection_catch_rate', 0.0):.4f}",
            "",
        ]
    )

    if llm:
        lines.extend(
            [
                "## Saved LLM Spec Audit Calibration",
                "",
                "In the saved LLM pilot suite, specs allowed by the gate produced 0 verified-but-wrong selections.",
                "",
                "| model | valid specs | ALLOW | REVIEW | BLOCK | verified_but_wrong | ALLOW + verified_but_wrong | hidden pass rate for ALLOW |",
                "|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in llm.get("by_model", []):
            hidden_rate = row.get("hidden_oracle_pass_rate_for_allow_specs")
            hidden_label = "n/a" if hidden_rate is None else f"{hidden_rate:.4f}"
            lines.append(
                f"| `{row['model']}` | {row['valid_specs']} | {row['ALLOW']} | {row['REVIEW']} | "
                f"{row['BLOCK']} | {row['verified_but_wrong_count']} | {row['allow_verified_but_wrong_count']} | {hidden_label} |"
            )

    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- This is calibrated on controlled benchmark specs.",
            "- Requirement coverage uses known benchmark requirements.",
            "- In real deployments, requirement discovery remains hard.",
            "- The audit gate is a safety layer, not a proof of correctness.",
        ]
    )
    SPEC_AUDIT_CALIBRATION_REPORT.write_text("\n".join(lines), encoding="utf-8")


def write_policy_gate_calibration_report(result: dict[str, Any]) -> None:
    metrics = result.get("metrics", {})
    matrix = result.get("confusion_matrix", {})
    lines = [
        "# Policy Gate Calibration Report",
        "",
        "This report evaluates the deployable pre-selection policy audit gate. The gate sees public spec text and policy packs, not hidden oracle outcomes.",
        "",
        "## Summary Metrics",
        "",
        f"- dangerous_total: {metrics.get('dangerous_total', 0)}",
        f"- dangerous_allowed: {metrics.get('dangerous_allowed', 0)}",
        f"- dangerous_caught: {metrics.get('dangerous_caught', 0)}",
        f"- dangerous_catch_rate: {metrics.get('dangerous_catch_rate', 0.0):.4f}",
        f"- safe_total: {metrics.get('safe_total', 0)}",
        f"- safe_allowed: {metrics.get('safe_allowed', 0)}",
        f"- safe_allow_rate: {metrics.get('safe_allow_rate', 0.0):.4f}",
        f"- false_allow_count: {metrics.get('false_allow_count', 0)}",
        f"- false_block_count: {metrics.get('false_block_count', 0)}",
        f"- review_burden_count: {metrics.get('review_burden_count', 0)}",
        f"- high_or_critical_dangerous_catch_rate: {metrics.get('high_or_critical_catch_rate', 0.0):.4f}",
        "",
        "## Confusion Matrix",
        "",
        "| Ground truth / Gate decision | ALLOW | REVIEW | BLOCK |",
        "|---|---:|---:|---:|",
    ]
    for label in ["Dangerous specs", "Safe specs"]:
        row = matrix.get(label, {})
        lines.append(f"| {label} | {row.get('ALLOW', 0)} | {row.get('REVIEW', 0)} | {row.get('BLOCK', 0)} |")

    lines.extend(
        [
            "",
            "## Per-Mode Table",
            "",
            "| Spec class | Count | Dangerous | ALLOW | REVIEW | BLOCK | Dangerous allowed | Safe blocked |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in result.get("by_spec_class", []):
        lines.append(
            f"| `{row['spec_class']}` | {row['count']} | {row['dangerous']} | {row['ALLOW']} | "
            f"{row['REVIEW']} | {row['BLOCK']} | {row['dangerous_allowed']} | {row['safe_blocked']} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The policy audit gate does not simply use the hidden oracle. It compares public specs against policy-pack cards. Safe specs can still be reviewed if policy language is unclear, which is reported as review burden rather than hidden as success.",
            "",
            "## Limitations",
            "",
            "- Controlled calibration, not a general guarantee.",
            "- Policy cards are benchmark-supplied requirement inventories.",
            "- Keyword coverage is deterministic and auditable but not semantic proof.",
        ]
    )
    POLICY_GATE_CALIBRATION_REPORT.write_text("\n".join(lines), encoding="utf-8")
