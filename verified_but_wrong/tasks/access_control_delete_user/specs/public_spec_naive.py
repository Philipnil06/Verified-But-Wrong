def _actor(role: str = "admin", user_id: str = "u_admin") -> dict:
    return {"user_id": user_id, "role": role}


def _target(status: str = "active", user_id: str = "u_123") -> dict:
    return {"user_id": user_id, "status": status}


def _record(name: str, passed: bool, expected: str, actual: str) -> dict:
    return {"name": name, "passed": bool(passed), "expected": expected, "actual": actual}


def _summarize(tests: list[dict]) -> dict:
    failures = [
        f"{test['name']}: expected {test['expected']}, got {test['actual']}"
        for test in tests
        if not test["passed"]
    ]
    return {
        "passed": not failures,
        "passed_count": len(tests) - len(failures),
        "failed_count": len(failures),
        "failures": failures,
        "tests": tests,
    }


def run_tests(candidate_func) -> dict:
    tests = []
    result = candidate_func(_actor(), _target())
    updated = result.get("target") or {}
    tests.append(_record("admin_delete_active_target_ok", result.get("status") == "ok", "status=ok", f"status={result.get('status')}"))
    tests.append(_record("target_marked_deleted", updated.get("status") == "deleted", "target status=deleted", f"target status={updated.get('status')}"))
    return _summarize(tests)
