from __future__ import annotations

import importlib.util
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Any


CASE_DIR = Path(__file__).resolve().parent
CANDIDATES_DIR = CASE_DIR / "candidates"


def _load_module(path: Path, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_policy_card() -> dict[str, Any]:
    text = (CASE_DIR / "policy_pack.yaml").read_text(encoding="utf-8")

    def scalar(name: str) -> str:
        match = re.search(rf"^\s*(?:-\s*)?{re.escape(name)}:\s*(.+)$", text, re.MULTILINE)
        return match.group(1).strip() if match else ""

    def list_after(name: str) -> list[str]:
        match = re.search(rf"^\s*{re.escape(name)}:\s*\n((?:\s+- .+\n?)+)", text, re.MULTILINE)
        if not match:
            return []
        return [line.split("-", 1)[1].strip() for line in match.group(1).splitlines() if "-" in line]

    return {
        "id": scalar("id"),
        "title": scalar("title"),
        "category": scalar("category"),
        "severity": scalar("severity"),
        "requirement": scalar("requirement"),
        "applies_to": list_after("applies_to"),
        "failure_if_omitted": scalar("failure_if_omitted"),
        "audit_questions": list_after("audit_questions"),
        "keywords": list_after("keywords"),
        "suggested_spec_patch": scalar("suggested_spec_patch"),
    }


def _audit_public_spec(spec_text: str, policy_card: dict[str, Any]) -> dict[str, Any]:
    lowered = spec_text.lower()
    keyword_hits = [kw for kw in policy_card.get("keywords", []) if kw.lower() in lowered]
    covered = bool(keyword_hits)
    category = policy_card["category"]
    severity = policy_card["severity"]
    decision = "ALLOW" if covered else "BLOCK"
    return {
        "spec_source": "external_case_extracted_public_spec",
        "pre_selection_decision": decision,
        "coverage_rate": 1.0 if covered else 0.0,
        "covered_policy_cards": [policy_card] if covered else [],
        "missing_policy_cards": [] if covered else [policy_card],
        "critical_missing_requirements": [] if covered else [
            {
                "policy_card_id": policy_card["id"],
                "requirement": policy_card["requirement"],
                "category": category,
                "severity": severity,
                "why_it_matters": policy_card["failure_if_omitted"],
                "audit_question": policy_card.get("audit_questions", [""])[0],
            }
        ],
        "risk_categories": {} if covered else {category: 1},
        "severity_counts": {severity: 0 if covered else 1},
        "suggested_patches": [] if covered else [
            {
                "policy_card_id": policy_card["id"],
                "patch": policy_card["suggested_spec_patch"],
            }
        ],
        "recommendation": "Spec covers the role-downgrade session policy." if covered else "Block or repair before using this spec for implementation selection.",
        "ci_exit_code": 0 if covered else 1,
        "keyword_hits": keyword_hits,
    }


def _rank(candidate_results: list[dict[str, Any]], public_key: str) -> list[dict[str, Any]]:
    return sorted(
        candidate_results,
        key=lambda row: (
            not row[public_key]["passed"],
            -row[public_key]["passed_count"],
            row[public_key]["failed_count"],
            row["name"],
        ),
    )


def _policy_requirement_test(candidate_module: ModuleType) -> dict[str, Any]:
    public_tests = _load_module(CASE_DIR / "public_spec_tests.py", "external_public_spec_tests_policy")
    state = public_tests.make_state()
    downgrade = candidate_module.update_role(state, "user_1", "none")
    updated = downgrade.get("state", {})
    action = candidate_module.perform_admin_action(updated, "session_1")
    passed = action.get("allowed") is False
    return {
        "name": "role_downgrade_neutralizes_stale_privileged_session",
        "passed": passed,
        "expected": "old admin session denied after role downgrade",
        "actual": f"allowed={action.get('allowed')} message={action.get('message')}",
    }


def _run_repaired_public_tests(candidate_module: ModuleType) -> dict[str, Any]:
    public_tests = _load_module(CASE_DIR / "public_spec_tests.py", "external_public_spec_tests_repaired")
    result = public_tests.run_tests(candidate_module)
    tests = list(result["tests"])
    tests.append(_policy_requirement_test(candidate_module))
    failures = [test["name"] for test in tests if not test["passed"]]
    return {
        "passed": not failures,
        "passed_count": len(tests) - len(failures),
        "failed_count": len(failures),
        "failures": failures,
        "tests": tests,
    }


def _evaluate_candidates(use_repaired_spec: bool = False) -> dict[str, Any]:
    if str(CASE_DIR) not in sys.path:
        sys.path.insert(0, str(CASE_DIR))
    public_tests = _load_module(CASE_DIR / "public_spec_tests.py", "external_public_spec_tests")
    hidden_oracle = _load_module(CASE_DIR / "hidden_oracle.py", "external_hidden_oracle")

    candidate_rows = []
    for path in sorted(CANDIDATES_DIR.glob("impl_*.py")):
        module = _load_module(path, f"external_candidate_{path.stem}_{'repaired' if use_repaired_spec else 'public'}")
        public_result = _run_repaired_public_tests(module) if use_repaired_spec else public_tests.run_tests(module)
        hidden_result = hidden_oracle.run_tests(module)
        candidate_rows.append(
            {
                "name": path.name,
                "public": public_result,
                "hidden": hidden_result,
                "public_passed": public_result["passed"],
                "hidden_passed": hidden_result["passed"],
            }
        )

    ranked = _rank(candidate_rows, "public")
    selected = ranked[0]
    for row in candidate_rows:
        row["selected"] = row["name"] == selected["name"]
        row["verified_but_wrong"] = row["public_passed"] and not row["hidden_passed"] and row["selected"]

    return {
        "selected_candidate": selected["name"],
        "public_spec_passed": selected["public_passed"],
        "hidden_oracle_passed": selected["hidden_passed"],
        "verified_but_wrong": selected["public_passed"] and not selected["hidden_passed"],
        "candidates": candidate_rows,
    }


def _write_report(result: dict[str, Any]) -> None:
    gate = result["gate"]
    before = result["before_repair"]
    after = result["after_repair"]
    policy = result["policy_card"]
    lines = [
        "# Kibana Role Downgrade Session Invalidation Case Study",
        "",
        "## Framing",
        "",
        "This is an externally sourced public software-requirements artifact adapted into a minimal vericoding-style case study.",
        "",
        "We do not claim to reproduce the original Kibana bug. We adapt the public issue into a deterministic case study about stale privileged access after role downgrade.",
        "",
        "## Source",
        "",
        "- Repository: `elastic/kibana`",
        "- Issue: `#192346`",
        "- URL: https://github.com/elastic/kibana/issues/192346",
        "",
        "## Result",
        "",
        f"- before repair selected candidate: `{before['selected_candidate']}`",
        f"- before repair public spec passed: `{before['public_spec_passed']}`",
        f"- before repair hidden oracle passed: `{before['hidden_oracle_passed']}`",
        f"- before repair verified-but-wrong: `{before['verified_but_wrong']}`",
        f"- gate decision: `{gate['pre_selection_decision']}`",
        f"- missing policy: `{policy['id']}`",
        f"- category: `{policy['category']}`",
        f"- severity: `{policy['severity']}`",
        f"- after repair selected candidate: `{after['selected_candidate']}`",
        f"- after repair hidden oracle passed: `{after['hidden_oracle_passed']}`",
        f"- after repair verified-but-wrong: `{after['verified_but_wrong']}`",
        "",
        "## External Case Table",
        "",
        "| Case | Source | Omitted policy | Gate | Before repair | After repair |",
        "|---|---|---|---|---|---|",
        f"| Role downgrade session invalidation | Public GitHub issue | Active sessions after privilege downgrade | {gate['pre_selection_decision']} | {'VBW' if before['verified_but_wrong'] else 'pass'} | {'VBW' if after['verified_but_wrong'] else 'pass'} |",
        "",
        "## Gate Access Boundary",
        "",
        "The deployable audit gate sees only the extracted public spec and policy pack. It does not see the hidden oracle, selected candidate, or verified-but-wrong status.",
        "",
        "## Suggested Repair",
        "",
        gate["suggested_patches"][0]["patch"] if gate["suggested_patches"] else "No repair needed.",
    ]
    (CASE_DIR / "external_case_report.md").write_text("\n".join(lines), encoding="utf-8")


def run_case() -> dict[str, Any]:
    spec_text = (CASE_DIR / "extracted_public_spec.md").read_text(encoding="utf-8")
    policy_card = _load_policy_card()
    gate = _audit_public_spec(spec_text, policy_card)
    repaired_spec_text = spec_text.rstrip() + "\n\n## Policy Repair\n\n" + policy_card["suggested_spec_patch"] + "\n"

    before = _evaluate_candidates(use_repaired_spec=False)
    after = _evaluate_candidates(use_repaired_spec=True)
    result = {
        "result_type": "external_case_study",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "case_id": "kibana_role_downgrade_session_invalidation",
        "source": {
            "type": "externally sourced public GitHub issue",
            "repository": "elastic/kibana",
            "issue": 192346,
            "url": "https://github.com/elastic/kibana/issues/192346",
            "limitation": "adapted case study, not original bug reproduction",
        },
        "policy_card": policy_card,
        "gate": gate,
        "before_repair": before,
        "repair": {
            "patched_policy_card_ids": [policy_card["id"]],
            "repaired_spec_text": repaired_spec_text,
        },
        "after_repair": after,
    }
    (CASE_DIR / "results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_report(result)
    return result


if __name__ == "__main__":
    output = run_case()
    print("case:", output["case_id"])
    print("before_repair_verified_but_wrong:", output["before_repair"]["verified_but_wrong"])
    print("gate_result:", output["gate"]["pre_selection_decision"])
    print("after_repair_verified_but_wrong:", output["after_repair"]["verified_but_wrong"])
