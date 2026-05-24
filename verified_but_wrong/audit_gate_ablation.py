from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runner import RESULTS_DIR, list_tasks, run_task
from spec_audit_calibration import _mode_spec_text, _policy_gate_metrics
from spec_audit_gate import audit_public_spec


AUDIT_GATE_ABLATION_LATEST_JSON = RESULTS_DIR / "audit_gate_ablation_latest.json"
AUDIT_GATE_ABLATION_REPORT = RESULTS_DIR / "audit_gate_ablation_report.md"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _variant_decision(variant: str, audit: dict[str, Any]) -> str:
    if variant == "allow_all":
        return "ALLOW"
    if variant == "keyword_only":
        return "REVIEW" if audit["coverage_rate"] < 1.0 else "ALLOW"
    if variant == "coverage_threshold_only":
        return "REVIEW" if audit["critical_coverage_rate"] < 0.90 else "ALLOW"
    if variant == "category_only":
        return "BLOCK" if audit["critical_missing_requirements"] else "ALLOW"
    if variant == "severity_only":
        missing = audit["missing_policy_cards"]
        unclear = audit["unclear_policy_cards"]
        if any(card["severity"] == "critical" for card in missing):
            return "BLOCK"
        if any(card["severity"] in {"high", "critical"} for card in unclear + missing):
            return "REVIEW"
        return "ALLOW"
    if variant == "policy_cards_no_severity":
        return "REVIEW" if audit["missing_policy_cards"] or audit["unclear_policy_cards"] else "ALLOW"
    if variant == "generic_policy_only":
        return audit["pre_selection_decision"]
    if variant == "no_unclear_handling":
        return "BLOCK" if audit["critical_missing_requirements"] else "ALLOW"
    if variant == "no_business_rule_cards":
        missing = [c for c in audit["missing_policy_cards"] if c.get("category") != "business_rule_omission"]
        return "BLOCK" if missing else "ALLOW"
    if variant == "task_policy_without_severity":
        return "BLOCK" if audit["missing_policy_cards"] else ("REVIEW" if audit["unclear_policy_cards"] else "ALLOW")
    if variant in {"task_policy_with_severity", "full_policy_audit_gate"}:
        return audit["pre_selection_decision"]
    return "ALLOW"


def _rows_for_variant(variant: str) -> list[dict[str, Any]]:
    rows = []
    for task in list_tasks():
        for mode in ["naive", "critic", "oracle"]:
            spec_text, source = _mode_spec_text(task, mode)
            packs = ["generic_critical_requirements"] if variant == "generic_policy_only" else task.get("policy_pack_ids")
            audit = audit_public_spec(task["id"], spec_text, policy_pack_ids=packs, mode=mode, spec_source=source)
            selection = run_task(task["id"], mode)
            rows.append(
                {
                    "task_id": task["id"],
                    "mode": mode,
                    "verified_but_wrong": selection["verified_but_wrong"],
                    "pre_selection_decision": _variant_decision(variant, audit),
                    "critical_missing_requirements": audit.get("critical_missing_requirements", []),
                    "critical_unclear_requirements": audit.get("critical_unclear_requirements", []),
                }
            )
    return rows


def run_audit_gate_ablation() -> dict[str, Any]:
    variants = [
        "allow_all",
        "keyword_only",
        "policy_cards_no_severity",
        "severity_only",
        "category_only",
        "no_unclear_handling",
        "no_business_rule_cards",
        "generic_policy_only",
        "task_policy_with_severity",
        "full_policy_audit_gate",
    ]
    rows = []
    for variant in variants:
        variant_rows = _rows_for_variant(variant)
        metrics = _policy_gate_metrics(variant_rows)
        rows.append(
            {
                "variant": variant,
                "dangerous_catch_rate": metrics["dangerous_catch_rate"],
                "dangerous_allowed": metrics["dangerous_allowed"],
                "dangerous_caught": metrics["dangerous_caught"],
                "safe_allow_rate": metrics["safe_allow_rate"],
                "safe_block_rate": metrics["safe_block_rate"],
                "review_burden": metrics["review_burden_count"],
                "high_or_critical_dangerous_catch_rate": metrics["high_or_critical_catch_rate"],
                "high_or_critical_dangerous_allowed": metrics["high_or_critical_dangerous_total"] - metrics["high_or_critical_dangerous_caught"],
                "main_failure_mode": "allows dangerous specs" if metrics["dangerous_allowed"] else "review/block burden",
            }
        )
    result = {"result_type": "audit_gate_ablation", "timestamp": _timestamp(), "variants": rows}
    _write_json(AUDIT_GATE_ABLATION_LATEST_JSON, result)
    write_audit_gate_ablation_report(result)
    return result


def write_audit_gate_ablation_report(result: dict[str, Any]) -> None:
    lines = [
        "# Audit Gate Ablation Report",
        "",
        "| Gate variant | Dangerous allowed | Dangerous catch rate | Safe allow rate | Review burden | Failure mode |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in result["variants"]:
        lines.append(
            f"| `{row['variant']}` | {row['dangerous_allowed']} | {row['dangerous_catch_rate']:.4f} | "
            f"{row['safe_allow_rate']:.4f} | {row['review_burden']} | {row['main_failure_mode']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The ablation compares trivial and weaker gates with the full policy audit gate. Review burden is reported explicitly rather than hidden.",
        ]
    )
    AUDIT_GATE_ABLATION_REPORT.write_text("\n".join(lines), encoding="utf-8")
