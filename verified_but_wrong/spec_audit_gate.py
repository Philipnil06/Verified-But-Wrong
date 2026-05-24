from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from llm_specs import LLM_SPEC_RUNS_JSONL
from policy_pack import default_policy_pack_ids, load_policy_cards
from runner import BASE_DIR, RESULTS_DIR, load_task


SPEC_AUDIT_GATE_LATEST_JSON = RESULTS_DIR / "spec_audit_gate_latest.json"
SPEC_AUDIT_GATE_RUNS_JSONL = RESULTS_DIR / "spec_audit_gate_runs.jsonl"
SPEC_AUDIT_GATE_REPORT = RESULTS_DIR / "spec_audit_gate_report.md"
LLM_SELECTION_LATEST_JSON = RESULTS_DIR / "llm_selection_latest.json"

CRITICAL_CATEGORIES = {
    "security_omission",
    "authorization_omission",
    "idempotency_omission",
    "business_rule_omission",
    "state_invariant_omission",
    "conservation_omission",
}

HARD_BLOCK_CATEGORIES = {
    "security_omission",
    "authorization_omission",
    "tenant_isolation_omission",
    "audit_log_omission",
    "idempotency_omission",
    "business_rule_omission",
    "state_invariant_omission",
    "conservation_omission",
}

HIGH_SEVERITIES = {"high", "critical"}
STOPWORDS = {
    "must",
    "should",
    "with",
    "when",
    "that",
    "this",
    "from",
    "only",
    "unless",
    "before",
    "after",
    "during",
    "without",
    "state",
    "spec",
    "rule",
}


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


def _selection_index() -> dict[tuple[str, str, int], dict[str, Any]]:
    latest = _load_json(LLM_SELECTION_LATEST_JSON) or {}
    index = {}
    for run in latest.get("runs", []):
        key = (str(run.get("model")), str(run.get("task_id")), int(run.get("sample_id") or 0))
        index[key] = run
    return index


def _why_it_matters(task_id: str, requirement: str) -> str:
    text = requirement.lower()
    if task_id == "payment_webhook_idempotency" or "event_id" in text:
        return "Duplicate payment events may double-credit merchant balances."
    if task_id == "refund_window_expiry" or "30 days" in text:
        return "Refunds outside finance policy may be incorrectly approved."
    if task_id == "loyalty_refund_reversal" or "loyalty" in text:
        return "Customer reward balances may become financially inconsistent."
    if task_id == "access_control_delete_user":
        return "Unauthorized users may perform privileged destructive actions."
    if task_id == "rate_limiter_boundary":
        return "Abusive request bursts may be allowed past the intended limit."
    if "refund" in text:
        return "Refund behavior may violate payment conservation or state invariants."
    return "The generated spec may omit behavior that changes implementation selection risk."


def _review_question(task_id: str, requirement: str) -> str:
    if task_id == "loyalty_refund_reversal" and "loyalty" in requirement.lower():
        return "Does the spec explicitly state how loyalty points should be reversed during refunds?"
    if task_id == "payment_webhook_idempotency" and "event_id" in requirement.lower():
        return "Does the spec explicitly require duplicate event IDs to be ignored or processed once?"
    if task_id == "refund_window_expiry" and ("30 days" in requirement.lower() or "override" in requirement.lower()):
        return "Does the spec explicitly preserve the 30-day refund window and manual override exception?"
    if task_id == "access_control_delete_user":
        return "Does the spec explicitly restrict deletion to authorized admins and reject self-delete?"
    return f"Does the spec explicitly cover this requirement: {requirement}?"


def _enriched_items(task_id: str, task_categories: list[str], coverage_result: dict[str, Any], status: str) -> list[dict[str, Any]]:
    items = []
    for item in coverage_result.get("coverage", []):
        if item.get("status") != status:
            continue
        items.append(
            {
                "requirement": item.get("requirement"),
                "status": status,
                "categories": task_categories,
                "evidence": item.get("evidence", ""),
                "why_it_matters": _why_it_matters(task_id, str(item.get("requirement", ""))),
                "suggested_review_question": _review_question(task_id, str(item.get("requirement", ""))),
            }
        )
    return items


def _terms(text: str) -> list[str]:
    cleaned = (
        text.lower()
        .replace("-", " ")
        .replace("_", " ")
        .replace("/", " ")
        .replace(",", " ")
        .replace(".", " ")
    )
    return [word for word in cleaned.split() if len(word) >= 5 and word not in STOPWORDS]


def _policy_card_status(card: dict[str, Any], spec_text: str) -> tuple[str, str]:
    text = spec_text.lower()
    keywords = [str(keyword).lower() for keyword in card.get("keywords", [])]
    matches = [keyword for keyword in keywords if keyword in text]
    if matches:
        return "covered", ", ".join(matches[:4])

    related_terms = []
    for term in _terms(card.get("title", "") + " " + card.get("requirement", "")):
        if term in text and term not in related_terms:
            related_terms.append(term)
    if related_terms:
        return "unclear", "mentions related term(s): " + ", ".join(related_terms[:4])
    return "missing", "No matching policy keywords found."


def _policy_item(card: dict[str, Any], status: str, evidence: str, task_id: str) -> dict[str, Any]:
    audit_questions = card.get("audit_questions") or (
        [card.get("audit_question")] if card.get("audit_question") else []
    )
    review_question = audit_questions[0] if audit_questions else _review_question(task_id, card.get("requirement", ""))
    return {
        "policy_card_id": card["id"],
        "policy_pack_id": card.get("policy_pack_id"),
        "title": card.get("title"),
        "requirement": card.get("requirement"),
        "status": status,
        "category": card.get("category"),
        "categories": [card.get("category")] if card.get("category") else [],
        "severity": card.get("severity", "medium"),
        "evidence": evidence,
        "why_it_matters": card.get("why_it_matters") or _why_it_matters(task_id, card.get("requirement", "")),
        "suggested_spec_patch": card.get("suggested_spec_patch"),
        "suggested_review_question": review_question,
        "audit_question": review_question,
        "audit_questions": audit_questions,
        "requirement_test": card.get("requirement_test"),
    }


def _severity_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for item in items:
        severity = item.get("severity", "medium")
        counts.setdefault(severity, 0)
        counts[severity] += 1
    return counts


def _severity_rank(item: dict[str, Any]) -> int:
    severity = item.get("severity", "medium")
    return {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(severity, 4)


def _prioritized_policy_findings(
    missing_policy_cards: list[dict[str, Any]],
    unclear_policy_cards: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    combined = [{**item, "_status_group": "missing"} for item in missing_policy_cards] + [
        {**item, "_status_group": "unclear"} for item in unclear_policy_cards
    ]
    return sorted(
        combined,
        key=lambda item: (
            0
            if item["_status_group"] == "missing" and item.get("severity") in HIGH_SEVERITIES
            else 1
            if item["_status_group"] == "unclear" and item.get("severity") in HIGH_SEVERITIES
            else 2
            if item["_status_group"] == "missing" and item.get("severity") == "medium"
            else 3
            if item["_status_group"] == "unclear" and item.get("severity") == "medium"
            else 4,
            _severity_rank(item),
            str(item.get("policy_card_id") or item.get("requirement")),
        ),
    )


def _decision(
    missing_policy_cards: list[dict[str, Any]],
    unclear_policy_cards: list[dict[str, Any]],
    critical_coverage_rate: float,
) -> tuple[str, str, int]:
    if any(card.get("severity") == "critical" for card in missing_policy_cards):
        return "BLOCK", "Block this spec before implementation selection; a critical policy requirement is missing.", 2
    if any(card.get("category") in HARD_BLOCK_CATEGORIES for card in missing_policy_cards):
        return "BLOCK", "Block this spec before implementation selection; a load-bearing policy requirement is missing.", 2
    if any(card.get("severity") in HIGH_SEVERITIES for card in unclear_policy_cards):
        return "REVIEW", "Require review or spec repair before trusting this spec for selection.", 1
    if critical_coverage_rate < 0.90:
        return "REVIEW", "Require review because high/critical policy coverage is below threshold.", 1
    if any(card.get("severity") == "high" for card in missing_policy_cards):
        return "REVIEW", "Require review because a high-severity policy requirement is missing.", 1
    return "ALLOW", "No critical policy gaps detected by this audit gate; selection may proceed.", 0


def audit_public_spec(
    task_id: str,
    spec_text: str,
    policy_pack_ids: list[str] | None = None,
    policy_cards: list[dict[str, Any]] | None = None,
    mode: str = "llm",
    selection_result: dict[str, Any] | None = None,
    post_selection: bool = False,
    spec_source: str = "public_spec_text",
    model: str | None = None,
    sample_id: int | None = None,
) -> dict[str, Any]:
    task = load_task(task_id)
    pack_ids = policy_pack_ids or task.get("policy_pack_ids") or default_policy_pack_ids(task_id)
    cards = policy_cards or load_policy_cards(task_id, pack_ids)
    checked = []
    for card in cards:
        status, evidence = _policy_card_status(card, spec_text)
        checked.append(_policy_item(card, status, evidence, task_id))

    covered = [item for item in checked if item["status"] == "covered"]
    missing = [item for item in checked if item["status"] == "missing"]
    unclear = [item for item in checked if item["status"] == "unclear"]
    important_cards = [item for item in checked if item.get("severity") in HIGH_SEVERITIES]
    important_covered = [item for item in important_cards if item["status"] == "covered"]
    coverage_rate = len(covered) / len(checked) if checked else 1.0
    critical_coverage_rate = len(important_covered) / len(important_cards) if important_cards else 1.0

    critical_missing = [
        item
        for item in missing
        if item.get("severity") in HIGH_SEVERITIES or item.get("category") in HARD_BLOCK_CATEGORIES
    ]
    critical_unclear = [
        item
        for item in unclear
        if item.get("severity") in HIGH_SEVERITIES or item.get("category") in HARD_BLOCK_CATEGORIES
    ]

    pre_selection_decision, recommendation, ci_exit_code = _decision(missing, unclear, critical_coverage_rate)
    verified_but_wrong = bool(selection_result and selection_result.get("verified_but_wrong"))
    post_selection_decision = None
    if post_selection or selection_result is not None:
        post_selection_decision = "BLOCK" if verified_but_wrong else pre_selection_decision

    risk_counter: Counter[str] = Counter()
    for item in missing + unclear:
        if item.get("category"):
            risk_counter.update([item["category"]])
    prioritized_findings = _prioritized_policy_findings(missing, unclear)

    not_clear = missing + unclear
    return {
        "timestamp": _timestamp(),
        "task_id": task_id,
        "task_title": task.get("title"),
        "mode": mode,
        "spec_source": spec_source,
        "policy_pack_ids": pack_ids,
        "policy_cards_checked": checked,
        "pre_selection_decision": pre_selection_decision,
        "post_selection_decision": post_selection_decision,
        "risk_level": post_selection_decision or pre_selection_decision,
        "coverage_rate": coverage_rate,
        "critical_coverage_rate": critical_coverage_rate,
        "missing_policy_cards": missing,
        "unclear_policy_cards": unclear,
        "covered_policy_cards": covered,
        "critical_missing_requirements": critical_missing,
        "critical_unclear_requirements": critical_unclear,
        "noncritical_missing_requirements": [item for item in missing if item not in critical_missing],
        "noncritical_unclear_requirements": [item for item in unclear if item not in critical_unclear],
        "risk_categories": dict(risk_counter.most_common()),
        "severity_counts": _severity_counts(not_clear),
        "prioritized_policy_findings": prioritized_findings,
        "suggested_patches": [
            item["suggested_spec_patch"] for item in not_clear if item.get("suggested_spec_patch")
        ],
        "audit_questions": [
            item["suggested_review_question"] for item in not_clear if item.get("suggested_review_question")
        ],
        "recommendation": recommendation,
        "ci_exit_code": ci_exit_code,
        "model": model,
        "sample_id": sample_id,
        "verified_but_wrong": verified_but_wrong,
        "selected_candidate": selection_result.get("selected_candidate") if selection_result else None,
        "selection_result_summary": {
            "selected_candidate": selection_result.get("selected_candidate"),
            "public_spec_passed": selection_result.get("public_spec_passed"),
            "hidden_oracle_passed": selection_result.get("hidden_oracle_passed"),
            "verified_but_wrong": selection_result.get("verified_but_wrong"),
        }
        if selection_result
        else None,
        "generated_spec_excerpt": spec_text[:600],
    }


def audit_spec(
    task_id: str,
    generated_spec_text: str,
    coverage_result: dict[str, Any],
    selection_result: dict[str, Any] | None = None,
    model: str | None = None,
    sample_id: int | None = None,
    mode: str = "llm",
    spec_source: str = "saved_llm_spec",
) -> dict[str, Any]:
    task = load_task(task_id)
    task_categories = list(task.get("spec_hole_categories", []))
    exact_missing = _enriched_items(task_id, task_categories, coverage_result, "missing")
    unclear = _enriched_items(task_id, task_categories, coverage_result, "unclear")
    critical_missing = [
        item for item in exact_missing if CRITICAL_CATEGORIES.intersection(item.get("categories", []))
    ]
    unclear_critical = [
        item for item in unclear if CRITICAL_CATEGORIES.intersection(item.get("categories", []))
    ]
    noncritical_missing = [
        item for item in exact_missing if not CRITICAL_CATEGORIES.intersection(item.get("categories", []))
    ]
    noncritical_unclear = [
        item for item in unclear if not CRITICAL_CATEGORIES.intersection(item.get("categories", []))
    ]
    coverage_rate = coverage_result.get("clear_coverage_rate", coverage_result.get("coverage_rate", 0.0))
    verified_but_wrong = bool(selection_result and selection_result.get("verified_but_wrong"))

    if critical_missing:
        pre_selection_decision = "BLOCK"
        recommendation = "Block this spec before implementation selection; repair or review critical omissions first."
        ci_exit_code = 2
    elif unclear_critical or coverage_rate < 0.90:
        pre_selection_decision = "REVIEW"
        recommendation = "Require human review or spec repair before trusting this spec for selection."
        ci_exit_code = 1
    else:
        pre_selection_decision = "ALLOW"
        recommendation = "No critical gaps detected by this audit gate; selection may proceed."
        ci_exit_code = 0

    post_selection_decision = None
    if selection_result is not None:
        post_selection_decision = "BLOCK" if verified_but_wrong else pre_selection_decision

    critical_counter = Counter()
    for item in critical_missing + unclear_critical + noncritical_missing + noncritical_unclear:
        critical_counter.update(item.get("categories", []))

    return {
        "timestamp": _timestamp(),
        "task_id": task_id,
        "task_title": task.get("title"),
        "mode": mode,
        "spec_source": spec_source,
        "model": model,
        "sample_id": sample_id,
        "pre_selection_decision": pre_selection_decision,
        "post_selection_decision": post_selection_decision,
        "risk_level": post_selection_decision or pre_selection_decision,
        "coverage_rate": coverage_rate,
        "critical_missing_requirements": critical_missing,
        "critical_unclear_requirements": unclear_critical,
        "noncritical_missing_requirements": noncritical_missing,
        "noncritical_unclear_requirements": noncritical_unclear,
        "unclear_requirements": unclear,
        "risk_categories": dict(critical_counter.most_common()),
        "critical_categories": dict(critical_counter.most_common()),
        "verified_but_wrong": verified_but_wrong,
        "selected_candidate": selection_result.get("selected_candidate") if selection_result else None,
        "selection_result_summary": {
            "selected_candidate": selection_result.get("selected_candidate"),
            "public_spec_passed": selection_result.get("public_spec_passed"),
            "hidden_oracle_passed": selection_result.get("hidden_oracle_passed"),
            "verified_but_wrong": selection_result.get("verified_but_wrong"),
        }
        if selection_result
        else None,
        "recommendation": recommendation,
        "ci_exit_code": ci_exit_code,
        "generated_spec_excerpt": generated_spec_text[:600],
    }


def _summarize_model(model: str, audits: list[dict[str, Any]], invalid: int) -> dict[str, Any]:
    blocking_requirements: Counter[str] = Counter()
    review_requirements: Counter[str] = Counter()
    category_counter: Counter[str] = Counter()

    for audit in audits:
        for item in audit.get("critical_missing_requirements", []):
            blocking_requirements.update([item.get("requirement")])
            category_counter.update(item.get("categories", []))
        for item in audit.get("critical_unclear_requirements", []) + audit.get("unclear_policy_cards", []):
            review_requirements.update([item.get("requirement")])
            category_counter.update(item.get("categories", []))

    return {
        "model": model,
        "valid_specs": len(audits),
        "invalid_specs": invalid,
        "allow_count": sum(1 for audit in audits if audit["pre_selection_decision"] == "ALLOW"),
        "review_count": sum(1 for audit in audits if audit["pre_selection_decision"] == "REVIEW"),
        "block_count": sum(1 for audit in audits if audit["pre_selection_decision"] == "BLOCK"),
        "most_common_blocking_requirements": dict(blocking_requirements.most_common()),
        "most_common_review_requirements": dict(review_requirements.most_common()),
        "most_common_risk_categories": dict(category_counter.most_common()),
    }


def run_spec_audit_gate_on_saved_llm_specs() -> dict[str, Any]:
    rows = _load_jsonl(LLM_SPEC_RUNS_JSONL)
    selection_by_key = _selection_index()
    audits = []
    invalid_by_model: Counter[str] = Counter()
    audits_by_model: dict[str, list[dict[str, Any]]] = {}

    for row in rows:
        model = str(row.get("model") or "unknown")
        if not _is_valid_llm_generation(row):
            invalid_by_model.update([model])
            continue
        key = (model, str(row.get("task_id")), int(row.get("sample_id") or 0))
        audit = audit_public_spec(
            task_id=row["task_id"],
            spec_text=row.get("public_spec") or "",
            policy_pack_ids=None,
            selection_result=selection_by_key.get(key),
            model=model,
            sample_id=row.get("sample_id"),
            mode="llm",
            spec_source="results/llm_spec_runs.jsonl",
            post_selection=True,
        )
        audits.append(audit)
        audits_by_model.setdefault(model, []).append(audit)

    model_summaries = [
        _summarize_model(model, audits_by_model.get(model, []), invalid_by_model[model])
        for model in sorted(set(audits_by_model) | set(invalid_by_model))
    ]
    result = {
        "result_type": "spec_audit_gate",
        "timestamp": _timestamp(),
        "source": str(LLM_SPEC_RUNS_JSONL.relative_to(BASE_DIR)),
        "total_saved_rows": len(rows),
        "valid_specs": len(audits),
        "invalid_specs": sum(invalid_by_model.values()),
        "models": model_summaries,
        "audits": audits,
    }
    _write_json(SPEC_AUDIT_GATE_LATEST_JSON, result)
    _append_jsonl(SPEC_AUDIT_GATE_RUNS_JSONL, audits)
    write_spec_audit_gate_report(result)
    return result


def load_latest_spec_audit_gate() -> dict[str, Any] | None:
    return _load_json(SPEC_AUDIT_GATE_LATEST_JSON)


def write_spec_audit_gate_report(result: dict[str, Any]) -> None:
    audits = result.get("audits", [])
    example_block = next((audit for audit in audits if audit["pre_selection_decision"] == "BLOCK"), None)
    example_review = next((audit for audit in audits if audit["pre_selection_decision"] == "REVIEW"), None)
    example_allow = next((audit for audit in audits if audit["pre_selection_decision"] == "ALLOW"), None)

    lines = [
        "# Spec Audit Gate Report",
        "",
        "## Purpose",
        "",
        "The Spec Audit Gate converts coverage gaps into deployment-style decisions before a vericoding pipeline is allowed to select or accept an implementation.",
        "",
        "## Risk Rules",
        "",
        "- BLOCK if a critical requirement is exactly missing.",
        "- Pre-selection BLOCK if a critical requirement is exactly missing.",
        "- REVIEW if a critical requirement is unclear.",
        "- REVIEW if clear coverage rate is below 0.90.",
        "- ALLOW if no critical gaps are detected and coverage is above threshold.",
        "- Post-selection BLOCK can additionally be triggered by verified-but-wrong selection; this is for evaluation, not deployment gating.",
        "",
        "## Summary by Model",
        "",
        "| model | valid specs | invalid specs | ALLOW | REVIEW | BLOCK |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for model in result.get("models", []):
        lines.append(
            f"| `{model['model']}` | {model['valid_specs']} | {model['invalid_specs']} | "
            f"{model['allow_count']} | {model['review_count']} | {model['block_count']} |"
        )

    lines.extend(["", "## Per-Task Audit Examples", ""])
    for audit in audits[:20]:
        lines.append(
            f"- pre=`{audit['pre_selection_decision']}` post=`{audit.get('post_selection_decision')}` `{audit['model']}` `{audit['task_id']}` sample {audit['sample_id']}: "
            f"coverage={audit['coverage_rate']:.2f}, selected={audit.get('selected_candidate')}"
        )

    def add_example(title: str, audit: dict[str, Any] | None) -> None:
        lines.extend(["", f"## {title}", ""])
        if audit is None:
            lines.append("No saved audit example was available for this decision level.")
            return
        lines.extend(
            [
                f"- task: `{audit['task_id']}`",
                f"- model: `{audit['model']}`",
                f"- sample: `{audit['sample_id']}`",
                f"- pre-selection decision: `{audit['pre_selection_decision']}`",
                f"- post-selection decision: `{audit.get('post_selection_decision')}`",
                f"- recommendation: {audit['recommendation']}",
                f"- CI exit code: `{audit['ci_exit_code']}`",
            ]
        )
        if audit.get("critical_missing_requirements"):
            lines.append("- critical missing requirements:")
            for item in audit["critical_missing_requirements"][:5]:
                lines.append(f"  - {item['requirement']} ({', '.join(item['categories'])})")
        if audit.get("critical_unclear_requirements") or audit.get("unclear_policy_cards"):
            lines.append("- unclear requirements:")
            for item in (audit.get("critical_unclear_requirements") or audit.get("unclear_policy_cards", []))[:5]:
                lines.append(f"  - {item['requirement']} ({', '.join(item['categories'])})")

    add_example("Example BLOCK Decision", example_block)
    add_example("Example REVIEW Decision", example_review)
    add_example("Example ALLOW Decision", example_allow)

    lines.extend(
        [
            "",
            "## CI/CD Use",
            "",
            "A CI job can run this gate before implementation selection. `ALLOW` permits selection, `REVIEW` escalates to a human/spec-repair step, and `BLOCK` prevents a spec-driven pipeline from verifying the wrong target.",
        ]
    )
    SPEC_AUDIT_GATE_REPORT.write_text("\n".join(lines), encoding="utf-8")
