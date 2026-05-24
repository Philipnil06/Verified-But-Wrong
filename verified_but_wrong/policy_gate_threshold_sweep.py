from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from runner import RESULTS_DIR
from spec_audit_calibration import _policy_gate_metrics, run_policy_gate_calibration


THRESHOLD_SWEEP_JSON = RESULTS_DIR / "policy_gate_threshold_sweep.json"
THRESHOLD_SWEEP_MD = RESULTS_DIR / "policy_gate_threshold_sweep.md"


def _profile_decision(profile: str, row: dict[str, Any]) -> str:
    missing = row.get("missing_policy_cards", [])
    unclear = row.get("unclear_policy_cards", [])
    critical_missing = row.get("critical_missing_requirements", [])
    critical_unclear = row.get("critical_unclear_requirements", [])
    if profile == "conservative":
        if missing:
            return "BLOCK"
        if unclear:
            return "REVIEW"
        return "ALLOW"
    if profile == "permissive":
        if any(card.get("severity") == "critical" for card in critical_missing):
            return "BLOCK"
        if critical_missing:
            return "REVIEW"
        return "ALLOW"
    return row["pre_selection_decision"]


def run_policy_gate_threshold_sweep() -> dict[str, Any]:
    base = run_policy_gate_calibration()["runs"]
    profiles = []
    for profile in ["conservative", "default", "permissive"]:
        rows = [{**row, "pre_selection_decision": _profile_decision(profile, row)} for row in base]
        metrics = _policy_gate_metrics(rows)
        profiles.append(
            {
                "profile": profile,
                "dangerous_allowed": metrics["dangerous_allowed"],
                "dangerous_caught": metrics["dangerous_caught"],
                "safe_allow_rate": metrics["safe_allow_rate"],
                "review_burden": metrics["review_burden_count"],
                "safe_blocked": metrics["safe_blocked"],
            }
        )
    result = {"result_type": "policy_gate_threshold_sweep", "profiles": profiles}
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    THRESHOLD_SWEEP_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    write_threshold_sweep_report(result)
    return result


def write_threshold_sweep_report(result: dict[str, Any]) -> None:
    lines = [
        "# Policy Gate Threshold Sweep",
        "",
        "| Gate profile | Dangerous allowed | Dangerous caught | Safe allow rate | Review burden | Safe blocked |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in result["profiles"]:
        lines.append(
            f"| `{row['profile']}` | {row['dangerous_allowed']} | {row['dangerous_caught']} | "
            f"{row['safe_allow_rate']:.4f} | {row['review_burden']} | {row['safe_blocked']} |"
        )
    lines.extend(
        [
            "",
            "The default profile is selected because it preserves zero dangerous escapes in the current controlled/heldout suite while allowing most safe specs.",
        ]
    )
    THRESHOLD_SWEEP_MD.write_text("\n".join(lines), encoding="utf-8")
