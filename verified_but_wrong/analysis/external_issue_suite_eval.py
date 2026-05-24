from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from analysis.common import EXTERNAL_CASES_DIR, REPORTS_DIR, timestamp, write_json, write_markdown
from llm_selection import BASELINE_REQUIREMENTS, run_candidate_ranking_with_requirement_tests
from runner import run_task
from spec_audit_gate import audit_public_spec
from spec_repair import repair_spec_from_audit


EXTERNAL_KIBANA_DIR = Path(__file__).resolve().parent.parent.parent / "external_case_studies" / "kibana_role_downgrade_session_invalidation"
EXTERNAL_ISSUE_SUITE_JSON = REPORTS_DIR / "external_issue_suite_eval.json"
EXTERNAL_ISSUE_SUITE_MD = REPORTS_DIR / "external_issue_suite_eval.md"


def _requirements_from_cards(task_id: str, covered_policy_cards: list[dict[str, Any]]) -> list[str]:
    requirements = []
    baseline = BASELINE_REQUIREMENTS.get(task_id, {}).get("requirement")
    if baseline:
        requirements.append(baseline)
    for card in covered_policy_cards:
        requirement_test = card.get("requirement_test")
        if requirement_test and requirement_test not in requirements:
            requirements.append(requirement_test)
    return requirements


def _load_case_manifest(case_dir: Path) -> dict[str, Any]:
    return json.loads((case_dir / "case_manifest.json").read_text(encoding="utf-8"))


def _load_case_policy_cards(case_dir: Path) -> list[dict[str, Any]]:
    payload = json.loads((case_dir / "policy_card.json").read_text(encoding="utf-8"))
    return list(payload.get("policy_cards", []))


def _evaluate_local_case(case_dir: Path) -> dict[str, Any]:
    manifest = _load_case_manifest(case_dir)
    task_id = manifest["benchmark_task_id"]
    public_spec = (case_dir / manifest["public_spec_path"]).read_text(encoding="utf-8")
    policy_cards = _load_case_policy_cards(case_dir)

    before = run_task(task_id, "naive")
    gate = audit_public_spec(
        task_id=task_id,
        spec_text=public_spec,
        policy_cards=policy_cards,
        policy_pack_ids=[],
        mode="external_adapted",
        spec_source=str((case_dir / manifest["public_spec_path"]).relative_to(case_dir.parent.parent)),
        post_selection=False,
    )
    repaired = repair_spec_from_audit(public_spec, gate)
    after_audit = audit_public_spec(
        task_id=task_id,
        spec_text=repaired["repaired_spec_text"],
        policy_cards=policy_cards,
        policy_pack_ids=[],
        mode="external_repaired",
        spec_source=f"repair:{manifest['public_spec_path']}",
        post_selection=False,
    )
    selected_requirements = _requirements_from_cards(task_id, after_audit["covered_policy_cards"])
    after = run_candidate_ranking_with_requirement_tests(task_id, selected_requirements)

    return {
        "case_id": manifest["case_id"],
        "source_url": manifest["source_url"],
        "source_type": manifest["source_type"],
        "benchmark_task_id": task_id,
        "omitted_policy_ids": [card["id"] for card in policy_cards],
        "before_repair": {
            "selected_candidate": before["selected_candidate"],
            "public_spec_passed": before["public_spec_passed"],
            "hidden_oracle_passed": before["hidden_oracle_passed"],
            "verified_but_wrong": before["verified_but_wrong"],
        },
        "gate": {
            "pre_selection_decision": gate["pre_selection_decision"],
            "missing_policy_ids": [item["policy_card_id"] for item in gate["missing_policy_cards"]],
            "unclear_policy_ids": [item["policy_card_id"] for item in gate["unclear_policy_cards"]],
        },
        "after_repair": {
            "selected_candidate": after["selected_candidate"],
            "public_spec_passed": after["public_spec_passed"],
            "hidden_oracle_passed": after["hidden_oracle_passed"],
            "verified_but_wrong": after["verified_but_wrong"],
            "selected_requirements": selected_requirements,
        },
        "limitation": manifest["limitation"],
    }


def _evaluate_kibana_case() -> dict[str, Any]:
    results = json.loads((EXTERNAL_KIBANA_DIR / "results.json").read_text(encoding="utf-8"))
    return {
        "case_id": "kibana_role_downgrade_session_invalidation",
        "source_url": results["source"]["url"],
        "source_type": "externally sourced public GitHub issue adapted into a minimal vericoding-style case",
        "benchmark_task_id": "role_downgrade_session_invalidation",
        "omitted_policy_ids": [item["id"] for item in results["gate"].get("missing_policy_cards", [])],
        "before_repair": results["before_repair"],
        "gate": {
            "pre_selection_decision": results["gate"]["pre_selection_decision"],
            "missing_policy_ids": [item["id"] for item in results["gate"].get("missing_policy_cards", [])],
            "unclear_policy_ids": [item["id"] for item in results["gate"].get("unclear_policy_cards", [])],
        },
        "after_repair": results["after_repair"],
        "limitation": "Adapted case study, not a Kibana bug reproduction.",
    }


def write_external_issue_suite_report(result: dict[str, Any]) -> None:
    lines = [
        "# External Issue Suite Evaluation",
        "",
        "This suite uses externally sourced public issue patterns adapted into minimal vericoding-style cases. These are not bug reproductions and not prevalence estimates.",
        "",
        "| Case | Public source | Omitted policy | Before repair VBW | Gate | After repair |",
        "|---|---|---|---|---|---|",
    ]
    for case in result["cases"]:
        lines.append(
            f"| `{case['case_id']}` | {case['source_url']} | "
            f"{', '.join(case['omitted_policy_ids'])} | "
            f"{'yes' if case['before_repair']['verified_but_wrong'] else 'no'} | "
            f"`{case['gate']['pre_selection_decision']}` | "
            f"{'cleared' if not case['after_repair']['verified_but_wrong'] else 'still VBW'} |"
        )
    lines.extend(
        [
            "",
            "## Framing",
            "",
            "- externally sourced adapted issue suite",
            "- public software issue patterns",
            "- not bug reproductions",
            "- toy candidates and hidden oracles are authored for evaluation",
        ]
    )
    write_markdown(EXTERNAL_ISSUE_SUITE_MD, "\n".join(lines))


def run_external_issue_suite_eval() -> dict[str, Any]:
    cases = [_evaluate_kibana_case()]
    for case_dir in sorted(EXTERNAL_CASES_DIR.iterdir(), key=lambda path: path.name):
        if not case_dir.is_dir() or case_dir.name.startswith("_"):
            continue
        cases.append(_evaluate_local_case(case_dir))

    result = {
        "result_type": "external_issue_suite_eval",
        "timestamp": timestamp(),
        "total_cases": len(cases),
        "cases": cases,
    }
    write_json(EXTERNAL_ISSUE_SUITE_JSON, result)
    write_external_issue_suite_report(result)
    return result


if __name__ == "__main__":
    run_external_issue_suite_eval()
