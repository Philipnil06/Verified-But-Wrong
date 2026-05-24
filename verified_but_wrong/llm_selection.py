from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from llm_specs import LLM_SPEC_RUNS_JSONL
from runner import (
    BASE_DIR,
    RESULTS_DIR,
    get_task_dir,
    list_candidate_paths,
    list_tasks,
    load_module,
    load_task,
    rank_candidates,
)


LLM_SELECTION_RUNS_JSONL = RESULTS_DIR / "llm_selection_runs.jsonl"
LLM_SELECTION_LATEST_JSON = RESULTS_DIR / "llm_selection_latest.json"
FINAL_LLM_SELECTION_REPORT = RESULTS_DIR / "final_llm_selection_report.md"


BASELINE_REQUIREMENTS = {
    "refund_double_refund": {
        "requirement": "Valid positive refund on paid order succeeds",
        "keywords": ["refund", "positive", "paid", "success", "ok"],
    },
    "access_control_delete_user": {
        "requirement": "Admin can delete active target",
        "keywords": ["admin", "delete", "target", "active"],
    },
    "discount_nonnegative_price": {
        "requirement": "Normal discount works",
        "keywords": ["discount", "price", "final price", "percent"],
    },
    "rate_limiter_boundary": {
        "requirement": "First request is allowed",
        "keywords": ["request", "allow", "allowed", "rate"],
    },
    "expiry_handle_today": {
        "requirement": "Item expiring today is handle_today",
        "keywords": ["expiry", "expire", "today", "handle_today"],
    },
    "payment_webhook_idempotency": {
        "requirement": "Successful payment events should increase merchant balance",
        "keywords": ["successful", "payment", "balance", "amount", "increase"],
    },
    "refund_window_expiry": {
        "requirement": "Valid paid order refund succeeds",
        "keywords": ["refund", "paid", "order", "amount", "eligible"],
    },
    "loyalty_refund_reversal": {
        "requirement": "Valid refund succeeds",
        "keywords": ["refund", "paid", "order", "amount", "successful"],
    },
    "tenant_isolation_export": {
        "requirement": "Valid tenant export succeeds",
        "keywords": ["export", "records", "tenant", "filters"],
    },
    "role_downgrade_session_invalidation": {
        "requirement": "Valid role update succeeds",
        "keywords": ["role", "update", "user"],
    },
    "audit_log_retention_delete_user": {
        "requirement": "Valid delete succeeds",
        "keywords": ["delete", "user", "admin"],
    },
    "invoice_cancellation_stock_restore": {
        "requirement": "Valid cancellation succeeds",
        "keywords": ["cancel", "invoice", "order"],
    },
}


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def _load_requirement_tests(task_id: str) -> dict[str, Any]:
    task_dir = get_task_dir(task_id)
    module = load_module(
        task_dir / "requirement_tests" / "requirement_tests.py",
        f"{task_id}_requirement_tests",
    )
    return dict(module.REQUIREMENT_TESTS)


def _aggregate_tests(test_results: list[dict[str, Any]]) -> dict[str, Any]:
    failures = [
        f"{test['name']}: expected {test['expected']}, got {test['actual']}"
        for test in test_results
        if not test["passed"]
    ]
    return {
        "passed": not failures,
        "passed_count": len(test_results) - len(failures),
        "failed_count": len(failures),
        "failures": failures,
        "tests": test_results,
    }


def build_public_spec_from_coverage(task_id: str, coverage_result: dict) -> dict[str, Any]:
    available_tests = _load_requirement_tests(task_id)
    selected = []
    for item in coverage_result.get("coverage", []):
        requirement = item.get("requirement")
        if item.get("status") == "covered" and requirement in available_tests:
            selected.append(requirement)

    return {
        "task_id": task_id,
        "selected_requirements": selected,
        "empty_or_invalid_spec": len(selected) == 0,
    }


def _baseline_requirement_for_text(task_id: str, public_spec: str) -> str | None:
    baseline = BASELINE_REQUIREMENTS.get(task_id)
    if not baseline:
        return None
    text = public_spec.lower()
    if any(keyword in text for keyword in baseline["keywords"]):
        return baseline["requirement"]
    return None


def _selected_requirements_for_saved_row(row: dict[str, Any]) -> list[str]:
    task_id = row["task_id"]
    selected = build_public_spec_from_coverage(task_id, row.get("analysis", {}))["selected_requirements"]
    baseline = _baseline_requirement_for_text(task_id, row.get("public_spec") or "")
    if baseline and baseline not in selected:
        selected.insert(0, baseline)
    return selected


def _candidate_function(task: dict[str, Any], candidate_path: Path, index: int):
    module = load_module(candidate_path, f"{task['id']}_llm_selection_candidate_{index}_{candidate_path.stem}")
    return getattr(module, task["entrypoint"])


def evaluate_candidates_with_requirement_tests(task_id: str, selected_requirements: list[str]) -> dict[str, Any]:
    task = load_task(task_id)
    requirement_tests = _load_requirement_tests(task_id)
    selected_tests = [
        (requirement, requirement_tests[requirement])
        for requirement in selected_requirements
        if requirement in requirement_tests
    ]

    task_dir = get_task_dir(task_id)
    hidden_oracle_module = load_module(task_dir / "specs" / "hidden_oracle.py", f"{task_id}_llm_selection_hidden")
    candidate_results = []

    for index, candidate_path in enumerate(list_candidate_paths(task_dir)):
        candidate_func = _candidate_function(task, candidate_path, index)
        public_tests = [test_func(candidate_func) for _, test_func in selected_tests]
        public_result = _aggregate_tests(public_tests)
        hidden_result = hidden_oracle_module.run_tests(candidate_func)
        candidate_results.append(
            {
                "name": candidate_path.name,
                "public": public_result,
                "hidden": hidden_result,
                "public_passed": bool(public_result["passed"]),
                "hidden_passed": bool(hidden_result["passed"]),
                "selected": False,
                "verified_but_wrong": False,
            }
        )

    return {
        "task_id": task_id,
        "selected_requirements": selected_requirements,
        "empty_or_invalid_spec": not selected_tests,
        "candidate_results": candidate_results,
    }


def run_candidate_ranking_with_requirement_tests(task_id: str, selected_requirements: list[str]) -> dict:
    evaluated = evaluate_candidates_with_requirement_tests(task_id, selected_requirements)
    candidate_results = evaluated["candidate_results"]
    if evaluated["empty_or_invalid_spec"]:
        return {
            "task_id": task_id,
            "selected_requirements": [],
            "empty_or_invalid_spec": True,
            "selected_candidate": None,
            "public_spec_passed": False,
            "hidden_oracle_passed": False,
            "verified_but_wrong": False,
            "candidate_results": candidate_results,
        }

    ranked = rank_candidates(candidate_results)
    selected_name = ranked[0]["name"]
    for candidate in candidate_results:
        candidate["selected"] = candidate["name"] == selected_name
        candidate["verified_but_wrong"] = (
            candidate["selected"] and candidate["public_passed"] and not candidate["hidden_passed"]
        )

    selected = next(candidate for candidate in candidate_results if candidate["selected"])
    return {
        "task_id": task_id,
        "selected_requirements": selected_requirements,
        "empty_or_invalid_spec": False,
        "selected_candidate": selected["name"],
        "public_spec_passed": selected["public_passed"],
        "hidden_oracle_passed": selected["hidden_passed"],
        "verified_but_wrong": selected["verified_but_wrong"],
        "candidate_results": candidate_results,
    }


def _not_covered_items(row: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in row.get("analysis", {}).get("coverage", [])
        if item.get("status") in {"missing", "unclear"}
    ]


def _run_summary(model: str, runs: list[dict[str, Any]], invalid_count: int) -> dict[str, Any]:
    total = len(runs)
    wrong = sum(1 for run in runs if run["verified_but_wrong"])
    hidden_pass = sum(1 for run in runs if run["hidden_oracle_passed"])
    requirement_counts = [len(run["selected_requirements"]) for run in runs]
    failed_tasks = Counter(run["task_id"] for run in runs if run["verified_but_wrong"])
    category_counter: Counter[str] = Counter()
    for run in runs:
        if run["verified_but_wrong"]:
            category_counter.update(run.get("not_clearly_covered_categories", []))

    return {
        "model": model,
        "valid_specs": total,
        "empty_or_invalid_specs": invalid_count,
        "verified_but_wrong_count": wrong,
        "verified_but_wrong_rate": wrong / total if total else 0.0,
        "hidden_oracle_pass_rate": hidden_pass / total if total else 0.0,
        "average_selected_requirement_count": sum(requirement_counts) / total if total else 0.0,
        "most_common_failed_tasks": dict(failed_tasks.most_common()),
        "most_common_missing_categories_for_wrong_selection": dict(category_counter.most_common()),
    }


def run_saved_llm_spec_selection_experiment() -> dict[str, Any]:
    rows = _load_jsonl(LLM_SPEC_RUNS_JSONL)
    grouped_valid: dict[str, list[dict[str, Any]]] = {}
    grouped_invalid: Counter[str] = Counter()
    runs = []

    for row in rows:
        model = row.get("model") or "unknown"
        if not _is_valid_llm_generation(row):
            grouped_invalid[model] += 1
            continue

        selected_requirements = _selected_requirements_for_saved_row(row)
        ranking = run_candidate_ranking_with_requirement_tests(row["task_id"], selected_requirements)
        run = {
            "timestamp": _timestamp(),
            "model": model,
            "task_id": row["task_id"],
            "task_title": row.get("task_title"),
            "sample_id": row.get("sample_id"),
            "generated_public_spec": row.get("public_spec"),
            "selected_requirements": selected_requirements,
            "selected_requirement_count": len(selected_requirements),
            "selected_candidate": ranking["selected_candidate"],
            "public_spec_passed": ranking["public_spec_passed"],
            "hidden_oracle_passed": ranking["hidden_oracle_passed"],
            "verified_but_wrong": ranking["verified_but_wrong"],
            "empty_or_invalid_spec": ranking["empty_or_invalid_spec"],
            "candidate_results": ranking["candidate_results"],
            "not_clearly_covered_requirements": _not_covered_items(row),
            "not_clearly_covered_categories": row.get("analysis", {}).get("not_clearly_covered_categories")
            or row.get("analysis", {}).get("missing_categories", []),
        }
        grouped_valid.setdefault(model, []).append(run)
        runs.append(run)

    model_summaries = []
    for model in sorted(set(grouped_valid) | set(grouped_invalid)):
        model_summaries.append(_run_summary(model, grouped_valid.get(model, []), grouped_invalid[model]))

    result = {
        "timestamp": _timestamp(),
        "total_specs": len(runs),
        "models": model_summaries,
        "runs": runs,
    }
    _append_jsonl(LLM_SELECTION_RUNS_JSONL, runs)
    _write_json(LLM_SELECTION_LATEST_JSON, result)
    write_final_llm_selection_report(result)
    return result


def load_latest_llm_selection_experiment() -> dict[str, Any] | None:
    if not LLM_SELECTION_LATEST_JSON.exists():
        return None
    return json.loads(LLM_SELECTION_LATEST_JSON.read_text(encoding="utf-8"))


def write_final_llm_selection_report(result: dict[str, Any]) -> None:
    lines = [
        "# Final LLM Spec to Selection Report",
        "",
        "This report is built from saved LLM-generated specs only. No LLM spec text is executed as code.",
        "",
        "## Summary by Model",
        "",
        "| model | valid_specs | invalid_specs | verified_but_wrong_count | verified_but_wrong_rate | hidden_oracle_pass_rate | avg selected requirements |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for model in result.get("models", []):
        lines.append(
            f"| `{model['model']}` | {model['valid_specs']} | {model['empty_or_invalid_specs']} | "
            f"{model['verified_but_wrong_count']} | {model['verified_but_wrong_rate']:.4f} | "
            f"{model['hidden_oracle_pass_rate']:.4f} | {model['average_selected_requirement_count']:.2f} |"
        )

    wrong_runs = [run for run in result.get("runs", []) if run["verified_but_wrong"]]
    correct_runs = [run for run in result.get("runs", []) if run["hidden_oracle_passed"]]

    lines.extend(["", "## Wrong Selection Examples", ""])
    if not wrong_runs:
        lines.append("No verified-but-wrong selections were found in the saved LLM selection experiment.")
    for run in wrong_runs[:10]:
        lines.extend(
            [
                f"### {run['model']} / {run['task_id']} / sample {run['sample_id']}",
                "",
                f"- selected candidate: `{run['selected_candidate']}`",
                f"- selected requirements: {len(run['selected_requirements'])}",
                f"- hidden oracle passed: `{run['hidden_oracle_passed']}`",
                "",
            ]
        )

    lines.extend(["", "## Correct Selection Examples", ""])
    for run in correct_runs[:10]:
        lines.extend(
            [
                f"### {run['model']} / {run['task_id']} / sample {run['sample_id']}",
                "",
                f"- selected candidate: `{run['selected_candidate']}`",
                f"- selected requirements: {len(run['selected_requirements'])}",
                f"- hidden oracle passed: `{run['hidden_oracle_passed']}`",
                "",
            ]
        )

    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- The requirement-to-test mapping is manually curated.",
            "- Coverage classification is rule-based.",
            "- This is a controlled harness, not a fully automatic spec compiler.",
            "- Hidden oracles approximate intended behavior.",
            "- LLM-generated specs are mapped to pre-written executable tests; generated text is never executed as code.",
        ]
    )
    FINAL_LLM_SELECTION_REPORT.write_text("\n".join(lines), encoding="utf-8")
