from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from llm_specs import LLM_SPEC_RUNS_JSONL
from runner import RESULTS_DIR, load_task
from spec_audit_gate import _review_question


MANUAL_COVERAGE_AUDIT_MD = RESULTS_DIR / "manual_coverage_audit.md"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _is_valid_llm_generation(row: dict[str, Any]) -> bool:
    return (
        row.get("generation_empty") is not True
        and row.get("generation_error") != "empty_generated_spec"
        and bool(str(row.get("public_spec") or "").strip())
    )


def _excerpt(text: str, max_len: int = 260) -> str:
    normalized = " ".join((text or "").split())
    if len(normalized) <= max_len:
        return normalized
    return normalized[: max_len - 3] + "..."


def generate_manual_coverage_audit() -> dict[str, Any]:
    rows = [row for row in _load_jsonl(LLM_SPEC_RUNS_JSONL) if _is_valid_llm_generation(row)]
    worksheet_rows = []
    by_model: Counter[str] = Counter()
    by_task: Counter[str] = Counter()
    by_category: Counter[str] = Counter()
    exact_missing = 0
    unclear = 0

    for row in rows:
        task = load_task(row["task_id"])
        categories = task.get("spec_hole_categories", [])
        for item in row.get("analysis", {}).get("coverage", []):
            status = item.get("status")
            if status not in {"missing", "unclear"}:
                continue
            if status == "missing":
                exact_missing += 1
            else:
                unclear += 1
            by_model.update([row.get("model") or "unknown"])
            by_task.update([row["task_id"]])
            by_category.update(categories)
            worksheet_rows.append(
                {
                    "model": row.get("model") or "unknown",
                    "task_id": row["task_id"],
                    "sample_id": row.get("sample_id"),
                    "requirement": item.get("requirement"),
                    "rule_based_classification": status,
                    "categories": categories,
                    "generated_spec_excerpt": _excerpt(row.get("public_spec") or ""),
                    "audit_question": _review_question(row["task_id"], str(item.get("requirement", ""))),
                    "rule_based_evidence": item.get("evidence", ""),
                    "manual_judgment_placeholder": "TODO: covered / missing / unclear",
                    "notes_placeholder": "TODO",
                }
            )

    result = {
        "result_type": "manual_coverage_audit",
        "timestamp": _timestamp(),
        "total_exact_missing_requirements": exact_missing,
        "total_unclear_requirements": unclear,
        "by_model": dict(by_model.most_common()),
        "by_task": dict(by_task.most_common()),
        "by_category": dict(by_category.most_common()),
        "worksheet_rows": worksheet_rows,
        "path": str(MANUAL_COVERAGE_AUDIT_MD),
    }
    write_manual_coverage_audit(result)
    return result


def write_manual_coverage_audit(result: dict[str, Any]) -> None:
    lines = [
        "# Manual Coverage Audit Worksheet",
        "",
        "This worksheet is generated from rule-based exact-missing and unclear classifications. It is not a completed human audit.",
        "",
        "## Summary",
        "",
        f"- total exact missing requirements: {result['total_exact_missing_requirements']}",
        f"- total unclear requirements: {result['total_unclear_requirements']}",
        "",
        "### By Model",
        "",
    ]
    for key, value in result.get("by_model", {}).items():
        lines.append(f"- `{key}`: {value}")

    lines.extend(["", "### By Task", ""])
    for key, value in result.get("by_task", {}).items():
        lines.append(f"- `{key}`: {value}")

    lines.extend(["", "### By Category", ""])
    for key, value in result.get("by_category", {}).items():
        lines.append(f"- `{key}`: {value}")

    lines.extend(
        [
            "",
            "## Worksheet",
            "",
            "| model | task_id | sample_id | requirement | rule classification | categories | generated spec excerpt | audit question | rule evidence | manual judgment | notes |",
            "|---|---|---:|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in result.get("worksheet_rows", []):
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['model']}`",
                    f"`{row['task_id']}`",
                    str(row["sample_id"]),
                    str(row["requirement"]).replace("|", "\\|"),
                    row["rule_based_classification"],
                    ", ".join(f"`{category}`" for category in row["categories"]),
                    row["generated_spec_excerpt"].replace("|", "\\|"),
                    row["audit_question"].replace("|", "\\|"),
                    row["rule_based_evidence"].replace("|", "\\|"),
                    row["manual_judgment_placeholder"],
                    row["notes_placeholder"],
                ]
            )
            + " |"
        )
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    MANUAL_COVERAGE_AUDIT_MD.write_text("\n".join(lines), encoding="utf-8")
