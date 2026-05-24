def _record(name: str, passed: bool, expected: str, actual: str) -> dict:
    return {"name": name, "passed": bool(passed), "expected": expected, "actual": actual}


def _summarize(tests: list[dict]) -> dict:
    failures = [f"{test['name']}: expected {test['expected']}, got {test['actual']}" for test in tests if not test["passed"]]
    return {"passed": not failures, "passed_count": len(tests) - len(failures), "failed_count": len(failures), "failures": failures, "tests": tests}


def _run_sequence(candidate_func, user_id: str, timestamps: list[int]) -> tuple[list[dict], dict]:
    state = {}
    results = []
    for timestamp in timestamps:
        result = candidate_func(state, user_id, timestamp)
        results.append(result)
        state = result.get("state") or {}
    return results, state


def run_tests(candidate_func) -> dict:
    tests = []
    results, state = _run_sequence(candidate_func, "u1", [0, 10, 20, 30, 40])
    tests.append(_record("first_five_requests_allowed", all(result.get("allowed") is True for result in results), "all first five allowed=True", f"allowed={[result.get('allowed') for result in results]}"))

    sixth = candidate_func(state, "u1", 50)
    sixth_state = sixth.get("state") or {}
    tests.append(_record("sixth_request_blocked", sixth.get("allowed") is False, "allowed=False", f"allowed={sixth.get('allowed')}"))
    tests.append(_record("blocked_request_not_appended", 50 not in sixth_state.get("u1", []), "timestamp 50 not appended", f"u1 state={sixth_state.get('u1')}"))

    other_user = candidate_func(sixth_state, "u2", 51)
    tests.append(_record("different_user_independent", other_user.get("allowed") is True, "allowed=True for u2", f"allowed={other_user.get('allowed')}"))

    expired = candidate_func({"u1": [0, 10, 20, 30, 40]}, "u1", 70)
    expired_state = expired.get("state") or {}
    tests.append(_record("old_requests_expire_after_60_seconds", expired.get("allowed") is True and 0 not in expired_state.get("u1", []), "allowed=True and timestamp 0 expired", f"allowed={expired.get('allowed')}, u1 state={expired_state.get('u1')}"))
    return _summarize(tests)
