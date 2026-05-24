from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from policy_pack import POLICY_PACKS_DIR, load_policy_cards
from runner import RESULTS_DIR, TASKS_DIR, list_tasks
from spec_audit_gate import audit_public_spec

PROJECT_DIR = Path(__file__).resolve().parent
EXTERNAL_CASE_DIR = PROJECT_DIR.parent / "external_case_studies" / "kibana_role_downgrade_session_invalidation"
EXTERNAL_CASE_RESULTS = EXTERNAL_CASE_DIR / "results.json"
EXTERNAL_CASES_DIR = PROJECT_DIR / "external_cases"


def _load(path: str) -> dict[str, Any]:
    return json.loads((RESULTS_DIR / path).read_text(encoding="utf-8"))


def generate_policy_pack_index() -> dict[str, Any]:
    rows = []
    provenance = []
    for pack_path in sorted(POLICY_PACKS_DIR.glob("*.json")):
        pack = json.loads(pack_path.read_text(encoding="utf-8"))
        provenance.append(
            {
                "policy_pack": pack["id"],
                "source_type": "benchmark_author_defined",
                "intended_use": "pre-selection audit requirement inventory",
                "not_hidden_oracle": True,
                "gate_access_allowed": True,
            }
        )
        for card in pack.get("policy_cards", []):
            rows.append(
                {
                    "policy_card_id": card["id"],
                    "category": card.get("category"),
                    "severity": card.get("severity"),
                    "applies_to": ", ".join(card.get("applies_to", [])),
                    "why_it_matters": card.get("why_it_matters", ""),
                }
            )
    lines = [
        "# Policy Pack Index",
        "",
        "| Policy card ID | Category | Severity | Applies to | Why it matters |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['policy_card_id']}` | `{row['category']}` | {row['severity']} | {row['applies_to']} | {row['why_it_matters']} |"
        )
    (RESULTS_DIR / "policy_pack_index.md").write_text("\n".join(lines), encoding="utf-8")

    prov_lines = [
        "# Policy Pack Provenance",
        "",
        "| Pack | Source type | Intended use | Not hidden oracle | Gate access allowed |",
        "|---|---|---|---|---|",
    ]
    for row in provenance:
        prov_lines.append(
            f"| `{row['policy_pack']}` | {row['source_type']} | {row['intended_use']} | {row['not_hidden_oracle']} | {row['gate_access_allowed']} |"
        )
    (RESULTS_DIR / "policy_pack_provenance.md").write_text("\n".join(prov_lines), encoding="utf-8")
    return {"rows": rows, "provenance": provenance}


def generate_provenance_table() -> dict[str, Any]:
    manifest = json.loads(Path("evaluation_manifest.json").read_text(encoding="utf-8"))
    adapted_cases = sum(1 for path in EXTERNAL_CASES_DIR.iterdir() if path.is_dir() and not path.name.startswith("_")) if EXTERNAL_CASES_DIR.exists() else 0
    external_count = adapted_cases + (1 if EXTERNAL_CASE_RESULTS.exists() else len(manifest["external_docs"]))
    rows = [
        {"suite": "controlled development tasks", "count": len(manifest["development_tasks"]), "source_type": "author-created executable tasks", "purpose": "development/calibration", "used_for_tuning": True, "heldout": False, "external": False},
        {"suite": "heldout executable tasks", "count": len(manifest["heldout_tasks"]), "source_type": "author-created executable tasks", "purpose": "heldout evaluation", "used_for_tuning": False, "heldout": True, "external": False},
        {"suite": "naturalistic product-ticket-style fixtures", "count": len(manifest["naturalistic_docs"]), "source_type": "author-created product-ticket-style fixtures", "purpose": "naturalistic validation", "used_for_tuning": False, "heldout": False, "external": False},
        {"suite": "external/public adapted issue suite", "count": external_count, "source_type": "externally sourced public GitHub issues adapted into minimal case studies", "purpose": "preliminary external validity check", "used_for_tuning": False, "heldout": True, "external": True},
        {"suite": "saved live LLM specs", "count": 0, "source_type": "saved model outputs", "purpose": "pilot", "used_for_tuning": False, "heldout": False, "external": False},
        {"suite": "CI/CD demo spec", "count": 2, "source_type": "minimal deployment fixture", "purpose": "CI demonstration", "used_for_tuning": False, "heldout": False, "external": False},
    ]
    (RESULTS_DIR / "provenance_table.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = ["# Provenance Table", "", "| Suite | Count | Source type | Purpose | Used for tuning? | Heldout? | External? |", "|---|---:|---|---|---|---|---|"]
    for row in rows:
        lines.append(
            f"| {row['suite']} | {row['count']} | {row['source_type']} | {row['purpose']} | {row['used_for_tuning']} | {row['heldout']} | {row['external']} |"
        )
    (RESULTS_DIR / "provenance_table.md").write_text("\n".join(lines), encoding="utf-8")
    return {"rows": rows}


def run_known_vs_unknown_policy_demo() -> dict[str, Any]:
    spec = "Refund amounts must be positive and cannot exceed the remaining paid amount. Successful refunds update refunded_total."
    known = audit_public_spec("loyalty_refund_reversal", spec, ["payments_policy", "business_logic_policy"], mode="naturalistic")
    unknown = audit_public_spec("loyalty_refund_reversal", spec, ["generic_critical_requirements"], mode="naturalistic")
    result = {
        "known_policy_decision": known["pre_selection_decision"],
        "known_missing": [card["policy_card_id"] for card in known["missing_policy_cards"]],
        "unknown_policy_decision": unknown["pre_selection_decision"],
        "unknown_missing": [card["policy_card_id"] for card in unknown["missing_policy_cards"]],
    }
    lines = [
        "# Known vs Unknown Policy Report",
        "",
        "Our gate is designed for known-but-omitted requirements, not unknown unknowns.",
        "",
        f"- with loyalty policy pack: `{result['known_policy_decision']}`, missing={result['known_missing']}",
        f"- without loyalty policy pack: `{result['unknown_policy_decision']}`, missing={result['unknown_missing']}",
        "",
        "If no policy, human, or system has written the requirement down, the audit gate cannot reliably catch it.",
    ]
    (RESULTS_DIR / "known_vs_unknown_policy_report.md").write_text("\n".join(lines), encoding="utf-8")
    return result


def write_results_sha256() -> None:
    files = [
        RESULTS_DIR / "benchmark_latest.json",
        RESULTS_DIR / "policy_gate_calibration_latest.json",
        RESULTS_DIR / "spec_repair_latest.json",
        RESULTS_DIR / "defense_baselines_latest.json",
        RESULTS_DIR / "audit_gate_ablation_latest.json",
        RESULTS_DIR / "naturalistic_experiment_latest.json",
        RESULTS_DIR / "stats_summary.json",
        PROJECT_DIR / "reports" / "candidate_set_underconstraint.json",
        PROJECT_DIR / "reports" / "noisy_policy_pack_eval.json",
        PROJECT_DIR / "reports" / "external_issue_suite_eval.json",
        PROJECT_DIR / "reports" / "formal_demo_result.json",
        PROJECT_DIR / "reports" / "llm_policy_split_eval.json",
        EXTERNAL_CASE_RESULTS,
    ]
    lines = []
    for path in files:
        if not path.exists():
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        try:
            display = path.relative_to(PROJECT_DIR)
        except ValueError:
            display = path.relative_to(PROJECT_DIR.parent)
        lines.append(f"{digest}  {display.as_posix()}")
    Path("RESULTS_SHA256.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_final_submission_materials() -> None:
    benchmark = _load("benchmark_latest.json")
    policy = _load("policy_gate_calibration_latest.json")
    repair = _load("spec_repair_latest.json")
    nat = _load("naturalistic_experiment_latest.json")
    baselines = _load("defense_baselines_latest.json")
    pm = policy["metrics"]
    naive, critic, oracle = benchmark["naive"], benchmark["critic"], benchmark["oracle"]
    repair_naive = next(row for row in repair["summaries"] if row["mode"] == "naive")
    repair_critic = next(row for row in repair["summaries"] if row["mode"] == "critic")
    external_section = ""
    if EXTERNAL_CASE_RESULTS.exists():
        external = json.loads(EXTERNAL_CASE_RESULTS.read_text(encoding="utf-8"))
        suite_count = sum(1 for path in EXTERNAL_CASES_DIR.iterdir() if path.is_dir() and not path.name.startswith("_")) if EXTERNAL_CASES_DIR.exists() else 0
        external_section = f"""
## Externally Sourced Case Study

We adapted a public Kibana RBAC issue into a minimal vericoding-style case study. We do not claim to reproduce the original bug. The extracted public spec captures role update behavior but omits the policy requirement that privilege-reducing role changes must invalidate or revalidate active sessions.

The same verified-but-wrong pattern appears: before repair the selected candidate is `{external['before_repair']['selected_candidate']}`, the public spec passes, and the hidden oracle fails. The policy gate returns `{external['gate']['pre_selection_decision']}` before implementation selection. Targeted repair adds the missing session-invalidation/revalidation policy and removes the failure.

| Case | Source | Omitted policy | Gate | Before repair | After repair |
|---|---|---|---|---|---|
| Role downgrade session invalidation | Public GitHub issue | Active sessions after privilege downgrade | {external['gate']['pre_selection_decision']} | {'VBW' if external['before_repair']['verified_but_wrong'] else 'pass'} | {'VBW' if external['after_repair']['verified_but_wrong'] else 'pass'} |

We additionally include an externally sourced adapted issue suite of {suite_count + 1} public issue-pattern cases in the reproduction artifacts. These remain sanity checks, not bug reproductions or prevalence claims.
"""
    paper = f"""# Verified but Wrong: Intent-Gap Auditing for Vericoding Pipelines

## Abstract

Spec-driven development and vericoding pipelines aim to make generated code safer by selecting implementations that satisfy written specifications. This shifts a central trust problem from code to the specification: if the public spec omits an intent-critical requirement, a pipeline may select code that is verified against the spec but wrong against intended behavior.

We introduce Verified-but-Wrong, an evaluation outcome for specification omission failures in vericoding pipelines. Our harness selects candidate implementations against a public spec, then evaluates the selected implementation against a hidden executable oracle representing intended behavior. We separate public specs from policy packs and hidden oracles: the deployable gate sees only public spec text and policy cards, while hidden oracles are evaluation-only.

In the current {naive['total_tasks']}-task executable suite, naive specs produce {naive['wrong_selections']}/{naive['total_tasks']} verified-but-wrong selections, checklist critic specs produce {critic['wrong_selections']}/{critic['total_tasks']}, and oracle specs produce {oracle['wrong_selections']}/{oracle['total_tasks']}. The policy audit gate catches {pm['dangerous_caught']}/{pm['dangerous_total']} dangerous specs and allows {pm['dangerous_allowed']}. Safe allow rate is {pm['safe_allow_rate']:.4f}. Policy-targeted repair reduces naive failures from {repair_naive['vbw_before_repair']} to {repair_naive['vbw_after_repair']} and critic failures from {repair_critic['vbw_before_repair']} to {repair_critic['vbw_after_repair']}. Naturalistic product-ticket-style fixtures show {nat['vbw_before']} verified-but-wrong selections before repair and {nat['vbw_after_repair']} after repair.

## Introduction

A refund implementation can pass every public test and still be wrong. If the public spec says to refund the customer but omits the organization's rule that loyalty points from the original purchase must be reversed proportionally, a spec-driven pipeline can select an implementation that is verified against the spec and wrong against intended behavior.

This is not primarily a code-generation failure. It is a verification-target failure.

## Failure Model

VBW = Pass(public_spec, selected_impl) AND Fail(hidden_oracle, selected_impl).

- Public spec: used for implementation selection.
- Policy pack / requirement inventory: organization-maintained rules available to the audit gate.
- Hidden executable oracle: evaluation-only behavior checks.
- Known omitted policy: written in a policy pack but absent from the public spec.
- Unknown missing intent: not present in any policy inventory; the gate cannot solve this.

## Harness

Public Spec -> Policy Audit Gate -> Candidate Selection -> Hidden Executable Oracle.

The audit gate does not discover unknown intent. It checks whether a public implementation spec preserves requirements from an independently maintained policy inventory.

## Key Tables

| mode | tasks | verified-but-wrong |
|---|---:|---:|
| naive | {naive['total_tasks']} | {naive['wrong_selections']} |
| critic | {critic['total_tasks']} | {critic['wrong_selections']} |
| oracle | {oracle['total_tasks']} | {oracle['wrong_selections']} |

| gate metric | value |
|---|---:|
| dangerous caught | {pm['dangerous_caught']} |
| dangerous allowed | {pm['dangerous_allowed']} |
| safe allow rate | {pm['safe_allow_rate']:.4f} |
| safe block rate | {pm['safe_block_rate']:.4f} |

| repair mode | before | after |
|---|---:|---:|
| naive | {repair_naive['vbw_before_repair']} | {repair_naive['vbw_after_repair']} |
| critic | {repair_critic['vbw_before_repair']} | {repair_critic['vbw_after_repair']} |

## What This Does Not Claim

- We do not claim current LLMs always omit critical requirements.
- We do not claim real-world prevalence.
- We do not solve unknown requirement discovery.
- We do not claim the gate guarantees correctness.
- We do not use the hidden oracle in deployable pre-selection audit.
- We do not model hazardous bio protocols.

## Safety-Critical Relevance

This work is software/system-safety oriented: access control, audit logs, redaction, chain-of-custody, approvals, sample tracking, lab inventory, and compliance workflows. We do not model hazardous biological protocols. We model the software failure class: safety-relevant requirements omitted from implementation specs before automated code selection.

{external_section}

## Limitations

The benchmark is controlled and partly author-created. Policy packs must exist. Coverage is rule-based. Hidden oracles approximate intended behavior. The audit gate is a risk filter, not proof of correctness.

## Conclusion

Verified is not correct when the specification is incomplete.
"""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "final_submission_paper.md").write_text(paper, encoding="utf-8")
    (RESULTS_DIR / "final_impact_report.md").write_text(paper.replace("# Verified but Wrong", "# Final Impact Report"), encoding="utf-8")
    (RESULTS_DIR / "final_submission_abstract.md").write_text(paper.split("## Introduction")[0], encoding="utf-8")
    (RESULTS_DIR / "final_submission_60_second_pitch.md").write_text(
        "Vericoding moves the failure surface from code to specifications. Verified but Wrong provides a benchmark, policy-pack audit gate, repair loop, baselines, ablations, and CI demo for catching intent gaps before spec-driven systems select code.\n",
        encoding="utf-8",
    )
    (RESULTS_DIR / "final_submission_judge_rebuttals.md").write_text(
        "## How does the gate know what is missing?\nIt checks public specs against separate policy packs, not hidden oracles.\n\n## Does it block everything?\nNo. Safe allow rate and safe block rate are reported.\n\n## Is repair circular?\nRepair is compared against no/generic/checklist/oracle baselines and uses policy cards, not hidden oracle code.\n",
        encoding="utf-8",
    )
    (RESULTS_DIR / "final_submission_tables.md").write_text(paper[paper.index("## Key Tables"):paper.index("## What This Does Not Claim")], encoding="utf-8")
    (RESULTS_DIR / "final_submission_demo_script.md").write_text("Run Streamlit, show loyalty case, policy gate confusion matrix, repair baselines, and CI demo.\n", encoding="utf-8")
    (RESULTS_DIR / "final_submission_one_page_summary.md").write_text(paper[:2200], encoding="utf-8")
    (RESULTS_DIR / "final_submission_checklist.md").write_text("- [x] policy packs\n- [x] heldout tasks\n- [x] naturalistic docs\n- [x] repair loop\n- [x] baselines\n- [x] ablations\n- [x] CI demo\n", encoding="utf-8")
