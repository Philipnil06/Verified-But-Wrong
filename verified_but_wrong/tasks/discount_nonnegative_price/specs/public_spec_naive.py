def _record(name: str, passed: bool, expected: str, actual: str) -> dict:
    return {"name": name, "passed": bool(passed), "expected": expected, "actual": actual}


def _close(actual, expected: float) -> bool:
    return actual is not None and abs(actual - expected) < 1e-9


def _summarize(tests: list[dict]) -> dict:
    failures = [f"{test['name']}: expected {test['expected']}, got {test['actual']}" for test in tests if not test["passed"]]
    return {"passed": not failures, "passed_count": len(tests) - len(failures), "failed_count": len(failures), "failures": failures, "tests": tests}


def run_tests(candidate_func) -> dict:
    tests = []
    ten = candidate_func(100.0, 10.0)
    tests.append(_record("price_100_discount_10_is_90", ten.get("status") == "ok" and _close(ten.get("final_price"), 90.0), "status=ok, final_price=90.0", f"status={ten.get('status')}, final_price={ten.get('final_price')}"))

    fifty = candidate_func(200.0, 50.0)
    tests.append(_record("price_200_discount_50_is_100", fifty.get("status") == "ok" and _close(fifty.get("final_price"), 100.0), "status=ok, final_price=100.0", f"status={fifty.get('status')}, final_price={fifty.get('final_price')}"))
    return _summarize(tests)
