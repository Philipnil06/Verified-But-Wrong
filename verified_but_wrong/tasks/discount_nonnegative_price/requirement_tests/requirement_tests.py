def _record(name: str, passed: bool, expected: str, actual: str) -> dict:
    return {"name": name, "passed": bool(passed), "expected": expected, "actual": actual}


def _close(actual, expected: float) -> bool:
    return actual is not None and abs(actual - expected) < 1e-9


def normal_discount_works(candidate_func) -> dict:
    result = candidate_func(100.0, 10.0)
    passed = result.get("status") == "ok" and _close(result.get("final_price"), 90.0)
    actual = f"status={result.get('status')}, final_price={result.get('final_price')}"
    return _record("normal_discount_works", passed, "status=ok, final_price=90.0", actual)


def price_non_negative(candidate_func) -> dict:
    result = candidate_func(-100.0, 10.0)
    return _record("price_must_be_non_negative", result.get("status") == "error", "status=error", f"status={result.get('status')}")


def discount_bounds(candidate_func) -> dict:
    low = candidate_func(100.0, -10.0)
    high = candidate_func(100.0, 150.0)
    passed = low.get("status") == "error" and high.get("status") == "error"
    actual = f"negative discount status={low.get('status')}, over discount status={high.get('status')}"
    return _record("discount_percent_between_0_and_100", passed, "both statuses=error", actual)


def final_price_never_negative(candidate_func) -> dict:
    result = candidate_func(100.0, 150.0)
    passed = result.get("status") == "error" or (result.get("final_price") is not None and result.get("final_price") >= 0)
    actual = f"status={result.get('status')}, final_price={result.get('final_price')}"
    return _record("final_price_never_negative", passed, "status=error or final_price>=0", actual)


def invalid_input_fails(candidate_func) -> dict:
    result = candidate_func(-100.0, 150.0)
    return _record("invalid_input_should_fail", result.get("status") == "error", "status=error", f"status={result.get('status')}")


REQUIREMENT_TESTS = {
    "Normal discount works": normal_discount_works,
    "Price must be non negative": price_non_negative,
    "Discount percent must be between 0 and 100": discount_bounds,
    "Final price must never be negative": final_price_never_negative,
    "Invalid input should fail": invalid_input_fails,
}
