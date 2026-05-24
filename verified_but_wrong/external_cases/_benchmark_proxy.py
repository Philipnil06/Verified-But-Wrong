from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from runner import BASE_DIR, load_module


TASKS_DIR = BASE_DIR / "tasks"


def candidate_function(task_id: str, candidate_filename: str, entrypoint: str) -> Callable[..., Any]:
    path = TASKS_DIR / task_id / "candidates" / candidate_filename
    module = load_module(path, f"external_{task_id}_{path.stem}")
    return getattr(module, entrypoint)


def public_run_tests(task_id: str, candidate_func: Callable[..., Any]) -> dict[str, Any]:
    path = TASKS_DIR / task_id / "specs" / "public_spec_naive.py"
    module = load_module(path, f"external_{task_id}_public_tests")
    return module.run_tests(candidate_func)


def hidden_run_tests(task_id: str, candidate_func: Callable[..., Any]) -> dict[str, Any]:
    path = TASKS_DIR / task_id / "specs" / "hidden_oracle.py"
    module = load_module(path, f"external_{task_id}_hidden_oracle")
    return module.run_tests(candidate_func)
