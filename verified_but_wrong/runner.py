from __future__ import annotations

import copy
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Any, Callable


BASE_DIR = Path(__file__).resolve().parent
TASKS_DIR = BASE_DIR / "tasks"
RESULTS_DIR = BASE_DIR / "results"
RESULTS_JSONL = RESULTS_DIR / "results.jsonl"
LATEST_RUN_JSON = RESULTS_DIR / "latest_run.json"
BENCHMARK_LATEST_JSON = RESULTS_DIR / "benchmark_latest.json"
DEFAULT_TASK_ID = "refund_double_refund"
VALID_MODES = {"naive", "critic", "oracle"}
TAXONOMY_KEYS = [
    "idempotency_omission",
    "business_rule_omission",
    "boundary_omission",
    "invalid_input_omission",
    "state_invariant_omission",
    "security_omission",
    "authorization_omission",
    "error_behavior_omission",
    "conservation_omission",
    "temporal_omission",
    "domain_rule_omission",
    "tenant_isolation_omission",
    "audit_log_omission",
    "session_invalidation_omission",
    "approval_workflow_omission",
    "data_redaction_omission",
]


def ensure_directories() -> None:
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    ensure_directories()
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)


def load_module(path: Path, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def list_tasks() -> list[dict[str, Any]]:
    ensure_directories()
    tasks = []
    for task_json in sorted(TASKS_DIR.glob("*/task.json"), key=lambda path: path.parent.name):
        tasks.append(load_json(task_json))
    return tasks


def load_task(task_id: str = DEFAULT_TASK_ID) -> dict[str, Any]:
    ensure_directories()
    task_path = TASKS_DIR / task_id / "task.json"
    if not task_path.exists():
        raise FileNotFoundError(f"Unknown task_id: {task_id}")
    task = load_json(task_path)
    task.setdefault("entrypoint", "refund")
    return task


def get_task_dir(task_id: str) -> Path:
    return TASKS_DIR / task_id


def get_spec_path(task_dir: Path, mode: str) -> Path:
    if mode == "naive":
        return task_dir / "specs" / "public_spec_naive.py"
    if mode == "critic":
        return task_dir / "specs" / "public_spec_critic.py"
    if mode == "oracle":
        oracle_path = task_dir / "specs" / "public_spec_oracle.py"
        if oracle_path.exists():
            return oracle_path
        return task_dir / "specs" / "public_spec_critic.py"
    raise ValueError("mode must be 'naive', 'critic', or 'oracle'")


def run_spec(spec_module: ModuleType, candidate_func: Callable[..., dict]) -> dict[str, Any]:
    return copy.deepcopy(spec_module.run_tests(candidate_func))


def list_candidate_paths(task_dir: Path) -> list[Path]:
    return sorted((task_dir / "candidates").glob("impl_*.py"), key=lambda path: path.name)


def evaluate_candidates(task: dict[str, Any], mode: str) -> list[dict[str, Any]]:
    task_dir = get_task_dir(task["id"])
    public_spec_module = load_module(get_spec_path(task_dir, mode), f"{task['id']}_public_spec_{mode}")
    hidden_oracle_module = load_module(task_dir / "specs" / "hidden_oracle.py", f"{task['id']}_hidden_oracle")
    entrypoint = task["entrypoint"]
    candidates = []

    for index, candidate_path in enumerate(list_candidate_paths(task_dir)):
        module = load_module(candidate_path, f"{task['id']}_candidate_{index}_{candidate_path.stem}")
        if not hasattr(module, entrypoint):
            raise AttributeError(f"{candidate_path.name} does not export {entrypoint}")

        candidate_func = getattr(module, entrypoint)
        public_result = run_spec(public_spec_module, candidate_func)
        hidden_result = run_spec(hidden_oracle_module, candidate_func)
        candidates.append(
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

    if not candidates:
        raise FileNotFoundError(f"No candidates found for task {task['id']}")
    return candidates


def rank_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        candidates,
        key=lambda candidate: (
            not candidate["public_passed"],
            -int(candidate["public"]["passed_count"]),
            int(candidate["public"]["failed_count"]),
            candidate["name"],
        ),
    )


def build_spec_hole_report(task: dict[str, Any], selected: dict[str, Any]) -> dict[str, Any]:
    hidden_failures = selected["hidden"].get("failures", [])
    first_failure = hidden_failures[0] if hidden_failures else task.get("expected_naive_failure", "")
    missing_requirements = task.get("missing_requirements", [])
    categories = task.get("spec_hole_categories", [])

    return {
        "summary": "Selected implementation passed the public spec but failed the hidden intent oracle.",
        "missing_requirement": "; ".join(missing_requirements[:2]) if missing_requirements else "Unspecified missing requirement.",
        "categories": categories,
        "counterexample": first_failure or task.get("expected_naive_failure", "Hidden oracle found a counterexample."),
        "hidden_failures": hidden_failures,
    }


def persist_result(result: dict[str, Any]) -> None:
    ensure_directories()
    with RESULTS_JSONL.open("a", encoding="utf-8") as file:
        file.write(json.dumps(result, ensure_ascii=False) + "\n")
    write_json(LATEST_RUN_JSON, result)


def _normalize_run_args(task_id: str, mode: str) -> tuple[str, str]:
    # Keeps old calls like run_task("naive") working while supporting run_task(task_id, mode).
    if task_id in VALID_MODES and mode == "naive":
        return DEFAULT_TASK_ID, task_id
    if mode not in VALID_MODES:
        raise ValueError("mode must be 'naive', 'critic', or 'oracle'")
    return task_id, mode


def run_task(task_id: str = DEFAULT_TASK_ID, mode: str = "naive") -> dict[str, Any]:
    task_id, mode = _normalize_run_args(task_id, mode)
    task = load_task(task_id)
    candidates = evaluate_candidates(task, mode)
    ranked = rank_candidates(candidates)
    selected_name = ranked[0]["name"]

    for candidate in candidates:
        candidate["selected"] = candidate["name"] == selected_name
        candidate["verified_but_wrong"] = (
            candidate["selected"] and candidate["public_passed"] and not candidate["hidden_passed"]
        )

    selected = next(candidate for candidate in candidates if candidate["selected"])
    verified_but_wrong = selected["verified_but_wrong"]
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task_id": task["id"],
        "task_title": task["title"],
        "mode": mode,
        "selected_candidate": selected["name"],
        "public_spec_passed": selected["public_passed"],
        "hidden_oracle_passed": selected["hidden_passed"],
        "verified_but_wrong": verified_but_wrong,
        "spec_hole_report": build_spec_hole_report(task, selected) if verified_but_wrong else {},
        "task": task,
        "candidates": candidates,
    }
    persist_result(result)
    return result


def run_comparison(task_id: str = DEFAULT_TASK_ID) -> dict[str, Any]:
    naive_result = run_task(task_id, "naive")
    critic_result = run_task(task_id, "critic")
    oracle_result = run_task(task_id, "oracle")
    return {
        "task_id": task_id,
        "naive": naive_result,
        "critic": critic_result,
        "oracle": oracle_result,
        "summary": {
            "naive_verified_but_wrong": naive_result["verified_but_wrong"],
            "critic_verified_but_wrong": critic_result["verified_but_wrong"],
            "oracle_verified_but_wrong": oracle_result["verified_but_wrong"],
            "defense_reduced_failure": naive_result["verified_but_wrong"]
            and not critic_result["verified_but_wrong"],
            "oracle_reduced_failure": naive_result["verified_but_wrong"]
            and not oracle_result["verified_but_wrong"],
        },
    }


def _summary_for_runs(runs: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(runs)
    wrong = sum(1 for run in runs if run["verified_but_wrong"])
    hidden_passes = sum(1 for run in runs if run["hidden_oracle_passed"])
    return {
        "total_tasks": total,
        "wrong_selections": wrong,
        "verified_but_wrong_rate": wrong / total if total else 0.0,
        "hidden_oracle_pass_rate": hidden_passes / total if total else 0.0,
        "selected_correct_count": hidden_passes,
    }


def _taxonomy_counts(tasks: list[dict[str, Any]]) -> dict[str, int]:
    counts = {key: 0 for key in TAXONOMY_KEYS}
    for task in tasks:
        for category in task.get("spec_hole_categories", []):
            counts.setdefault(category, 0)
            counts[category] += 1
    return counts


def run_mini_benchmark() -> dict[str, Any]:
    tasks = list_tasks()
    task_rows = []
    naive_runs = []
    critic_runs = []
    oracle_runs = []

    for task in tasks:
        naive = run_task(task["id"], "naive")
        critic = run_task(task["id"], "critic")
        oracle = run_task(task["id"], "oracle")
        naive_runs.append(naive)
        critic_runs.append(critic)
        oracle_runs.append(oracle)
        task_rows.append(
            {
                "task_id": task["id"],
                "task_title": task["title"],
                "naive_selected": naive["selected_candidate"],
                "naive_verified_but_wrong": naive["verified_but_wrong"],
                "critic_selected": critic["selected_candidate"],
                "critic_verified_but_wrong": critic["verified_but_wrong"],
                "oracle_selected": oracle["selected_candidate"],
                "oracle_verified_but_wrong": oracle["verified_but_wrong"],
                "defense_fixed": naive["verified_but_wrong"] and not critic["verified_but_wrong"],
                "oracle_fixed": naive["verified_but_wrong"] and not oracle["verified_but_wrong"],
                "naive_hidden_oracle_passed": naive["hidden_oracle_passed"],
                "critic_hidden_oracle_passed": critic["hidden_oracle_passed"],
                "oracle_hidden_oracle_passed": oracle["hidden_oracle_passed"],
            }
        )

    naive_summary = _summary_for_runs(naive_runs)
    critic_summary = _summary_for_runs(critic_runs)
    oracle_summary = _summary_for_runs(oracle_runs)
    benchmark = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tasks": task_rows,
        "naive": naive_summary,
        "critic": critic_summary,
        "oracle": oracle_summary,
        "improvement": {
            "wrong_selection_reduction": naive_summary["wrong_selections"] - critic_summary["wrong_selections"],
            "verified_but_wrong_rate_delta": naive_summary["verified_but_wrong_rate"]
            - critic_summary["verified_but_wrong_rate"],
            "hidden_oracle_pass_rate_delta": critic_summary["hidden_oracle_pass_rate"]
            - naive_summary["hidden_oracle_pass_rate"],
            "oracle_wrong_selection_reduction": naive_summary["wrong_selections"] - oracle_summary["wrong_selections"],
            "oracle_verified_but_wrong_rate_delta": naive_summary["verified_but_wrong_rate"]
            - oracle_summary["verified_but_wrong_rate"],
            "oracle_hidden_oracle_pass_rate_delta": oracle_summary["hidden_oracle_pass_rate"]
            - naive_summary["hidden_oracle_pass_rate"],
        },
        "taxonomy_counts": _taxonomy_counts(tasks),
    }
    write_json(BENCHMARK_LATEST_JSON, benchmark)
    return benchmark


def load_latest_result() -> dict[str, Any] | None:
    ensure_directories()
    if not LATEST_RUN_JSON.exists():
        return None
    return load_json(LATEST_RUN_JSON)


def load_latest_benchmark() -> dict[str, Any] | None:
    ensure_directories()
    if not BENCHMARK_LATEST_JSON.exists():
        return None
    return load_json(BENCHMARK_LATEST_JSON)


def load_results_log(limit: int = 10) -> list[dict[str, Any]]:
    ensure_directories()
    if not RESULTS_JSONL.exists():
        return []

    rows = []
    with RESULTS_JSONL.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if "mode" in row and "selected_candidate" in row:
                rows.append(row)
    return rows[-limit:][::-1]


if __name__ == "__main__":
    print(json.dumps(run_mini_benchmark(), indent=2, ensure_ascii=False))
