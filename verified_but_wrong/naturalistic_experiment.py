from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from llm_selection import BASELINE_REQUIREMENTS, run_candidate_ranking_with_requirement_tests
from runner import BASE_DIR, RESULTS_DIR
from spec_audit_gate import audit_public_spec
from spec_repair import repair_spec_from_audit


NATURALISTIC_DIR = BASE_DIR / "naturalistic_specs"
NATURALISTIC_EXPERIMENT_LATEST_JSON = RESULTS_DIR / "naturalistic_experiment_latest.json"
NATURALISTIC_EXPERIMENT_REPORT = RESULTS_DIR / "naturalistic_experiment_report.md"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _requirements_from_audit(task_id: str, audit: dict[str, Any]) -> list[str]:
    requirements = []
    baseline = BASELINE_REQUIREMENTS.get(task_id, {}).get("requirement")
    if baseline:
        requirements.append(baseline)
    for card in audit.get("covered_policy_cards", []):
        requirement_test = card.get("requirement_test")
        if requirement_test and requirement_test not in requirements:
            requirements.append(requirement_test)
    return requirements


def _load_doc(task_dir: Path) -> tuple[str, list[str]]:
    spec = (task_dir / "public_ticket.md").read_text(encoding="utf-8")
    policy_file = task_dir / "policy_pack.json"
    policy_pack_ids = json.loads(policy_file.read_text(encoding="utf-8")).get("policy_pack_ids", [])
    return spec, policy_pack_ids


def _provenance(task_dir: Path) -> dict[str, Any]:
    path = task_dir / "provenance.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "doc_id": task_dir.name,
        "task_id": task_dir.name,
        "source_type": "product-ticket-style fixture",
        "author": "benchmark_author",
        "external_url": None,
        "created_for": "naturalistic validation",
        "contains_hidden_policy_in_public_ticket": False,
        "policy_pack_accessible_to_gate": True,
        "hidden_oracle_accessible_to_gate": False,
    }


def _run_one(doc_id: str, task_dir: Path) -> dict[str, Any]:
    provenance = _provenance(task_dir)
    task_id = provenance.get("task_id", doc_id)
    spec_text, policy_pack_ids = _load_doc(task_dir)
    audit_before = audit_public_spec(
        task_id,
        spec_text,
        policy_pack_ids=policy_pack_ids,
        mode="naturalistic",
        spec_source=str((task_dir / "public_ticket.md").relative_to(BASE_DIR)),
    )
    before_requirements = _requirements_from_audit(task_id, audit_before)
    before_selection = run_candidate_ranking_with_requirement_tests(task_id, before_requirements)
    repair = repair_spec_from_audit(spec_text, audit_before)
    audit_after = audit_public_spec(
        task_id,
        repair["repaired_spec_text"],
        policy_pack_ids=policy_pack_ids,
        mode="repaired",
        spec_source=f"repair:{task_dir.name}",
    )
    after_requirements = _requirements_from_audit(task_id, audit_after)
    after_selection = run_candidate_ranking_with_requirement_tests(task_id, after_requirements)
    return {
        "task_id": task_id,
        "doc_id": doc_id,
        "provenance": provenance,
        "policy_pack_ids": policy_pack_ids,
        "audit_decision_before": audit_before["pre_selection_decision"],
        "audit_decision_after": audit_after["pre_selection_decision"],
        "selected_candidate_before": before_selection["selected_candidate"],
        "verified_but_wrong_before": before_selection["verified_but_wrong"],
        "selected_candidate_after": after_selection["selected_candidate"],
        "verified_but_wrong_after": after_selection["verified_but_wrong"],
        "requirements_before": before_requirements,
        "requirements_after": after_requirements,
        "repair": repair,
        "audit_before": audit_before,
        "audit_after": audit_after,
    }


def run_naturalistic_experiment() -> dict[str, Any]:
    rows = []
    for task_dir in sorted(path for path in NATURALISTIC_DIR.iterdir() if path.is_dir()):
        rows.append(_run_one(task_dir.name, task_dir))
    result = {
        "result_type": "naturalistic_experiment",
        "timestamp": _timestamp(),
        "naturalistic_docs_evaluated": len(rows),
        "dangerous_docs": sum(1 for row in rows if row["verified_but_wrong_before"]),
        "safe_docs": sum(1 for row in rows if not row["verified_but_wrong_before"]),
        "dangerous_caught": sum(
            1
            for row in rows
            if row["verified_but_wrong_before"] and row["audit_decision_before"] in {"REVIEW", "BLOCK"}
        ),
        "safe_allowed": sum(
            1
            for row in rows
            if not row["verified_but_wrong_before"] and row["audit_decision_before"] == "ALLOW"
        ),
        "safe_reviewed": sum(
            1
            for row in rows
            if not row["verified_but_wrong_before"] and row["audit_decision_before"] == "REVIEW"
        ),
        "safe_blocked": sum(
            1
            for row in rows
            if not row["verified_but_wrong_before"] and row["audit_decision_before"] == "BLOCK"
        ),
        "review_burden": sum(1 for row in rows if row["audit_decision_before"] in {"REVIEW", "BLOCK"}),
        "vbw_before": sum(1 for row in rows if row["verified_but_wrong_before"]),
        "vbw_after_repair": sum(1 for row in rows if row["verified_but_wrong_after"]),
        "dangerous_docs_allowed": sum(
            1
            for row in rows
            if row["audit_decision_before"] == "ALLOW" and row["verified_but_wrong_before"]
        ),
        "runs": rows,
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    NATURALISTIC_EXPERIMENT_LATEST_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    write_naturalistic_experiment_report(result)
    return result


def write_naturalistic_experiment_report(result: dict[str, Any]) -> None:
    lines = [
        "# Naturalistic Spec Experiment Report",
        "",
        f"- naturalistic docs evaluated: {result['naturalistic_docs_evaluated']}",
        f"- dangerous docs: {result['dangerous_docs']}",
        f"- safe docs: {result['safe_docs']}",
        f"- dangerous caught: {result['dangerous_caught']}",
        f"- safe allowed: {result['safe_allowed']}",
        f"- safe reviewed: {result['safe_reviewed']}",
        f"- safe blocked: {result['safe_blocked']}",
        f"- verified-but-wrong before audit/repair: {result['vbw_before']}",
        f"- verified-but-wrong after repair: {result['vbw_after_repair']}",
        f"- dangerous docs allowed by gate: {result['dangerous_docs_allowed']}",
        "",
        "| task | decision before | VBW before | decision after | VBW after | selected before | selected after |",
        "|---|---|---:|---|---:|---|---|",
    ]
    for row in result["runs"]:
        lines.append(
            f"| `{row['doc_id']}` -> `{row['task_id']}` | {row['audit_decision_before']} | {row['verified_but_wrong_before']} | "
            f"{row['audit_decision_after']} | {row['verified_but_wrong_after']} | "
            f"`{row['selected_candidate_before']}` | `{row['selected_candidate_after']}` |"
        )
    lines.extend(
        [
            "",
            "## Provenance",
            "",
            "| doc | task | source type | author | external url |",
            "|---|---|---|---|---|",
        ]
    )
    for row in result["runs"]:
        p = row.get("provenance", {})
        lines.append(
            f"| `{row['doc_id']}` | `{row['task_id']}` | {p.get('source_type')} | {p.get('author')} | {p.get('external_url')} |"
        )
    lines.extend(
        [
            "",
            "## Limitation",
            "",
            "These documents are hand-written product-ticket style fixtures. They are more naturalistic than one-line specs, but still controlled benchmark artifacts.",
        ]
    )
    NATURALISTIC_EXPERIMENT_REPORT.write_text("\n".join(lines), encoding="utf-8")
