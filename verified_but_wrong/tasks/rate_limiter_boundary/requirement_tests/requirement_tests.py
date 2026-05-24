def _record(name: str, passed: bool, expected: str, actual: str) -> dict:
    return {"name": name, "passed": bool(passed), "expected": expected, "actual": actual}


def _run_sequence(candidate_func, user_id: str, timestamps: list[int]) -> tuple[list[dict], dict]:
    state = {}
    results = []
    for timestamp in timestamps:
        result = candidate_func(state, user_id, timestamp)
        results.append(result)
        state = result.get("state") or {}
    return results, state


def first_request_allowed(candidate_func) -> dict:
    result = candidate_func({}, "u1", 0)
    return _record("first_request_allowed", result.get("allowed") is True, "allowed=True", f"allowed={result.get('allowed')}")


def sixth_request_blocked(candidate_func) -> dict:
    results, state = _run_sequence(candidate_func, "u1", [0, 10, 20, 30, 40])
    sixth = candidate_func(state, "u1", 50)
    passed = all(result.get("allowed") is True for result in results) and sixth.get("allowed") is False
    actual = f"first five={[result.get('allowed') for result in results]}, sixth={sixth.get('allowed')}"
    return _record("sixth_request_blocked", passed, "first five allowed=True, sixth allowed=False", actual)


def per_user_limit(candidate_func) -> dict:
    _, state = _run_sequence(candidate_func, "u1", [0, 10, 20, 30, 40])
    blocked = candidate_func(state, "u1", 50)
    other = candidate_func(blocked.get("state") or state, "u2", 51)
    return _record("limit_is_per_user", other.get("allowed") is True, "u2 allowed=True", f"u2 allowed={other.get('allowed')}")


def old_requests_expire(candidate_func) -> dict:
    result = candidate_func({"u1": [0, 10, 20, 30, 40]}, "u1", 70)
    state = result.get("state") or {}
    passed = result.get("allowed") is True and 0 not in state.get("u1", [])
    actual = f"allowed={result.get('allowed')}, u1 state={state.get('u1')}"
    return _record("old_requests_outside_60_seconds_expire", passed, "allowed=True and timestamp 0 expired", actual)


def boundary_at_five(candidate_func) -> dict:
    results, _ = _run_sequence(candidate_func, "u1", [0, 10, 20, 30, 40])
    return _record("boundary_at_exactly_five_requests", all(result.get("allowed") is True for result in results), "first five allowed=True", f"allowed={[result.get('allowed') for result in results]}")


REQUIREMENT_TESTS = {
    "First request is allowed": first_request_allowed,
    "The 6th request must be blocked": sixth_request_blocked,
    "The limit is per user, not global": per_user_limit,
    "Old requests outside 60 seconds must expire": old_requests_expire,
    "Boundary behavior at exactly 5 requests must be correct": boundary_at_five,
}
