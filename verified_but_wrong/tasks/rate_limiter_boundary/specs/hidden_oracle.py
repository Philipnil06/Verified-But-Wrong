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
    tests.append(_record("first_five_requests_inside_window_allowed", all(result.get("allowed") is True for result in results), "five allowed=True", f"allowed={[result.get('allowed') for result in results]}"))

    sixth = candidate_func(state, "u1", 50)
    sixth_state = sixth.get("state") or {}
    tests.append(_record("sixth_request_counterexample", sixth.get("allowed") is False, "6th request in 60 seconds allowed=False", f"allowed={sixth.get('allowed')}"))

    other_user = candidate_func(sixth_state, "u2", 51)
    tests.append(_record("per_user_independence_counterexample", other_user.get("allowed") is True, "different user allowed=True", f"allowed={other_user.get('allowed')}"))

    expired = candidate_func({"u1": [0, 10, 20, 30, 40]}, "u1", 70)
    expired_state = expired.get("state") or {}
    tests.append(_record("window_expiration_counterexample", expired.get("allowed") is True and 0 not in expired_state.get("u1", []), "old timestamp 0 expired and request allowed", f"allowed={expired.get('allowed')}, u1 state={expired_state.get('u1')}"))

    blocked = candidate_func({"u1": [0, 10, 20, 30, 40]}, "u1", 50)
    blocked_state = blocked.get("state") or {}
    tests.append(_record("blocked_request_does_not_update_state", blocked.get("allowed") is False and 50 not in blocked_state.get("u1", []), "blocked request not appended", f"allowed={blocked.get('allowed')}, u1 state={blocked_state.get('u1')}"))
    return _summarize(tests)
