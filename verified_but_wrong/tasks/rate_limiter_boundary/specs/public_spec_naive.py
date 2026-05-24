def _record(name: str, passed: bool, expected: str, actual: str) -> dict:
    return {"name": name, "passed": bool(passed), "expected": expected, "actual": actual}


def _summarize(tests: list[dict]) -> dict:
    failures = [f"{test['name']}: expected {test['expected']}, got {test['actual']}" for test in tests if not test["passed"]]
    return {"passed": not failures, "passed_count": len(tests) - len(failures), "failed_count": len(failures), "failures": failures, "tests": tests}


def run_tests(candidate_func) -> dict:
    tests = []
    first = candidate_func({}, "u1", 0)
    first_state = first.get("state") or {}
    tests.append(_record("first_request_allowed", first.get("allowed") is True, "allowed=True", f"allowed={first.get('allowed')}"))
    tests.append(_record("first_request_updates_user_state", 0 in first_state.get("u1", []), "state contains u1 timestamp 0", f"u1 state={first_state.get('u1')}"))

    second = candidate_func(first_state, "u1", 10)
    second_state = second.get("state") or {}
    tests.append(_record("second_normal_request_allowed", second.get("allowed") is True, "allowed=True", f"allowed={second.get('allowed')}"))
    tests.append(_record("second_request_updates_state", second_state.get("u1", []).count(10) == 1, "state contains u1 timestamp 10", f"u1 state={second_state.get('u1')}"))
    return _summarize(tests)
