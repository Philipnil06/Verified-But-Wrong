from __future__ import annotations

from collections import Counter
from typing import Any

from analysis.common import (
    PRIMARY_CAUSAL_POLICY_CARD,
    REPORTS_DIR,
    split_for_task,
    timestamp,
    write_json,
    write_markdown,
)
from policy_pack import default_policy_pack_ids, load_policy_cards
from policy_perturbations import add_irrelevant_noise, apply_outdated_wording, remove_causal_policy
from runner import list_tasks, run_task
from spec_audit_calibration import _mode_spec_text
from spec_audit_gate import audit_public_spec


NOISY_POLICY_PACK_EVAL_JSON = REPORTS_DIR / "noisy_policy_pack_eval.json"
NOISY_POLICY_PACK_EVAL_MD = REPORTS_DIR / "noisy_policy_pack_eval.md"

CONDITIONS = {
    "clean": "Current applicable policy cards.",
    "noisy_5x": "Adds 4 irrelevant policy cards for each relevant policy card.",
    "noisy_10x": "Adds 9 irrelevant policy cards for each relevant policy card.",
    "noisy_50x": "Adds 49 irrelevant policy cards for each relevant policy card.",
    "incomplete_25": "Removes the causally relevant omitted policy card for 25% of dangerous cases.",
    "incomplete_50": "Removes the causally relevant omitted policy card for 50% of dangerous cases.",
    "outdated_wording": "Weakens the wording and keywords of the causally relevant policy card.",
    "noisy_10x_plus_outdated": "Adds 9 irrelevant cards per relevant card and weakens the causally relevant policy card.",
}


def _base_rows() -> list[dict[str, Any]]:
    rows = []
    for task in list_tasks():
        for mode in ["naive", "critic", "oracle"]:
            spec_text, spec_source = _mode_spec_text(task, mode)
            selection_result = run_task(task["id"], mode)
            rows.append(
                {
                    "task_id": task["id"],
                    "task_title": task["title"],
                    "split": split_for_task(task["id"]),
                    "mode": mode,
                    "spec_text": spec_text,
                    "spec_source": spec_source,
                    "selection_result": selection_result,
                    "dangerous": selection_result["verified_but_wrong"],
                    "causal_policy_id": PRIMARY_CAUSAL_POLICY_CARD.get(task["id"]),
                    "policy_pack_ids": task.get("policy_pack_ids") or default_policy_pack_ids(task["id"]),
                    "base_cards": load_policy_cards(task["id"], task.get("policy_pack_ids") or default_policy_pack_ids(task["id"])),
                }
            )
    return rows


def _dangerous_drop_set(base_rows: list[dict[str, Any]], fraction: float) -> set[tuple[str, str]]:
    dangerous_keys = sorted((row["task_id"], row["mode"]) for row in base_rows if row["dangerous"])
    target = int(round(len(dangerous_keys) * fraction))
    return set(dangerous_keys[:target])


def _perturbed_cards(
    row: dict[str, Any],
    condition: str,
    drop_keys: set[tuple[str, str]],
) -> list[dict[str, Any]]:
    cards = row["base_cards"]
    causal_policy_id = row["causal_policy_id"]
    task_id = row["task_id"]
    key = (task_id, row["mode"])

    if condition == "clean":
        return cards
    if condition == "noisy_5x":
        return add_irrelevant_noise(task_id, cards, 5)
    if condition == "noisy_10x":
        return add_irrelevant_noise(task_id, cards, 10)
    if condition == "noisy_50x":
        return add_irrelevant_noise(task_id, cards, 50)
    if condition == "incomplete_25":
        return remove_causal_policy(cards, causal_policy_id) if key in drop_keys else cards
    if condition == "incomplete_50":
        return remove_causal_policy(cards, causal_policy_id) if key in drop_keys else cards
    if condition == "outdated_wording":
        return apply_outdated_wording(cards, causal_policy_id)
    if condition == "noisy_10x_plus_outdated":
        return apply_outdated_wording(add_irrelevant_noise(task_id, cards, 10), causal_policy_id)
    raise ValueError(f"Unknown policy perturbation condition: {condition}")


def _audit_rows_for_condition(base_rows: list[dict[str, Any]], condition: str) -> list[dict[str, Any]]:
    drop_keys = set()
    if condition == "incomplete_25":
        drop_keys = _dangerous_drop_set(base_rows, 0.25)
    elif condition == "incomplete_50":
        drop_keys = _dangerous_drop_set(base_rows, 0.50)

    rows = []
    for row in base_rows:
        cards = _perturbed_cards(row, condition, drop_keys)
        audit = audit_public_spec(
            task_id=row["task_id"],
            spec_text=row["spec_text"],
            policy_pack_ids=row["policy_pack_ids"],
            policy_cards=cards,
            mode=row["mode"],
            post_selection=False,
            spec_source=f"{condition}:{row['spec_source']}",
            selection_result=None,
        )
        prioritized = audit.get("prioritized_policy_findings", [])
        top_policy_ids = [item.get("policy_card_id") for item in prioritized[:3]]
        causal_policy_id = row["causal_policy_id"]
        rows.append(
            {
                "condition": condition,
                "task_id": row["task_id"],
                "task_title": row["task_title"],
                "split": row["split"],
                "mode": row["mode"],
                "dangerous": row["dangerous"],
                "causal_policy_id": causal_policy_id,
                "pre_selection_decision": audit["pre_selection_decision"],
                "missing_policy_card_ids": [item["policy_card_id"] for item in audit["missing_policy_cards"]],
                "unclear_policy_card_ids": [item["policy_card_id"] for item in audit["unclear_policy_cards"]],
                "top_policy_ids": top_policy_ids,
                "exact_causal_policy_identified_at_1": bool(causal_policy_id and top_policy_ids[:1] == [causal_policy_id]),
                "exact_causal_policy_identified_at_3": bool(causal_policy_id and causal_policy_id in top_policy_ids),
                "missing_policy_count": len(audit["missing_policy_cards"]),
                "review_item_count": len(prioritized),
                "policy_cards_checked": len(cards),
                "audit": audit,
            }
        )
    return rows


def _condition_summary(condition: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    dangerous_rows = [row for row in rows if row["dangerous"]]
    safe_rows = [row for row in rows if not row["dangerous"]]
    dangerous_allow = sum(1 for row in dangerous_rows if row["pre_selection_decision"] == "ALLOW")
    dangerous_review = sum(1 for row in dangerous_rows if row["pre_selection_decision"] == "REVIEW")
    dangerous_block = sum(1 for row in dangerous_rows if row["pre_selection_decision"] == "BLOCK")
    safe_allow = sum(1 for row in safe_rows if row["pre_selection_decision"] == "ALLOW")
    safe_review = sum(1 for row in safe_rows if row["pre_selection_decision"] == "REVIEW")
    safe_block = sum(1 for row in safe_rows if row["pre_selection_decision"] == "BLOCK")
    return {
        "condition": condition,
        "description": CONDITIONS[condition],
        "dangerous_total": len(dangerous_rows),
        "dangerous_allowed": dangerous_allow,
        "dangerous_caught": dangerous_review + dangerous_block,
        "dangerous_review": dangerous_review,
        "dangerous_block": dangerous_block,
        "safe_total": len(safe_rows),
        "safe_allowed": safe_allow,
        "safe_reviewed": safe_review,
        "safe_blocked": safe_block,
        "safe_allow_rate": safe_allow / len(safe_rows) if safe_rows else 0.0,
        "exact_causal_policy_identified_at_1": sum(
            1 for row in dangerous_rows if row["exact_causal_policy_identified_at_1"]
        ),
        "exact_causal_policy_identified_at_3": sum(
            1 for row in dangerous_rows if row["exact_causal_policy_identified_at_3"]
        ),
        "mean_number_of_missing_policies_reported": sum(row["missing_policy_count"] for row in rows) / len(rows),
        "mean_number_of_review_items": sum(row["review_item_count"] for row in rows) / len(rows),
        "review_burden": (safe_review + safe_block + dangerous_review + dangerous_block) / len(rows),
        "false_positive_rate_on_safe_specs": (safe_review + safe_block) / len(safe_rows) if safe_rows else 0.0,
        "false_negative_rate_on_dangerous_specs": dangerous_allow / len(dangerous_rows) if dangerous_rows else 0.0,
    }


def write_noisy_policy_pack_report(result: dict[str, Any]) -> None:
    lines = [
        "# Policy-Pack Robustness Evaluation",
        "",
        "This report perturbs the policy inventory while keeping the same 36 controlled spec instances fixed. It measures how the Policy Audit Gate trades off dangerous-spec recall against safe-spec allowance and review burden.",
        "",
        "## Policy-Pack Robustness",
        "",
        "| Policy pack condition | Dangerous allowed | Dangerous caught | Safe allow rate | Exact causal @1 | Exact causal @3 | Review burden |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["summaries"]:
        lines.append(
            f"| `{row['condition']}` | {row['dangerous_allowed']} | {row['dangerous_caught']} | "
            f"{row['safe_allow_rate']:.2%} | {row['exact_causal_policy_identified_at_1']} | "
            f"{row['exact_causal_policy_identified_at_3']} | {row['review_burden']:.2%} |"
        )

    lines.extend(["", "## Notes by Condition", ""])
    for row in result["summaries"]:
        lines.append(f"- `{row['condition']}`: {row['description']}")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Noisy policy packs may legitimately increase conservatism. Incomplete policy packs are expected to miss some dangerous specs because the causally relevant policy is no longer represented. This is a dependency claim, not a bug: the gate targets known-but-omitted policies.",
        ]
    )
    write_markdown(NOISY_POLICY_PACK_EVAL_MD, "\n".join(lines))


def run_noisy_policy_pack_eval() -> dict[str, Any]:
    base_rows = _base_rows()
    all_rows = []
    summaries = []
    for condition in CONDITIONS:
        rows = _audit_rows_for_condition(base_rows, condition)
        all_rows.extend(rows)
        summaries.append(_condition_summary(condition, rows))

    result = {
        "result_type": "noisy_policy_pack_eval",
        "timestamp": timestamp(),
        "spec_instances": len(base_rows),
        "conditions": list(CONDITIONS),
        "summaries": summaries,
        "rows": all_rows,
    }
    write_json(NOISY_POLICY_PACK_EVAL_JSON, result)
    write_noisy_policy_pack_report(result)
    return result


if __name__ == "__main__":
    run_noisy_policy_pack_eval()
