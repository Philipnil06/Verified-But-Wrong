def _record(name: str, passed: bool, expected: str, actual: str) -> dict:
    return {"name": name, "passed": bool(passed), "expected": expected, "actual": actual}


def _close(actual, expected: float) -> bool:
    return actual is not None and abs(actual - expected) < 1e-9


def _summarize(tests: list[dict]) -> dict:
    failures = [f"{test['name']}: expected {test['expected']}, got {test['actual']}" for test in tests if not test["passed"]]
    return {"passed": not failures, "passed_count": len(tests) - len(failures), "failed_count": len(failures), "failures": failures, "tests": tests}


def run_tests(candidate_func) -> dict:
    tests = []
    normal = candidate_func(100.0, 10.0)
    tests.append(_record("normal_discount_works", normal.get("status") == "ok" and _close(normal.get("final_price"), 90.0), "status=ok, final_price=90.0", f"status={normal.get('status')}, final_price={normal.get('final_price')}"))

    zero = candidate_func(100.0, 0.0)
    tests.append(_record("zero_discount_boundary", zero.get("status") == "ok" and _close(zero.get("final_price"), 100.0), "status=ok, final_price=100.0", f"status={zero.get('status')}, final_price={zero.get('final_price')}"))

    full = candidate_func(100.0, 100.0)
    tests.append(_record("hundred_percent_discount_boundary", full.get("status") == "ok" and _close(full.get("final_price"), 0.0), "status=ok, final_price=0.0", f"status={full.get('status')}, final_price={full.get('final_price')}"))

    over = candidate_func(100.0, 150.0)
    tests.append(_record("discount_over_100_counterexample", over.get("status") == "error", "status=error for discount 150", f"status={over.get('status')}, final_price={over.get('final_price')}"))

    negative_discount = candidate_func(100.0, -10.0)
    tests.append(_record("negative_discount_counterexample", negative_discount.get("status") == "error", "status=error for discount -10", f"status={negative_discount.get('status')}, final_price={negative_discount.get('final_price')}"))

    negative_price = candidate_func(-100.0, 10.0)
    tests.append(_record("negative_price_counterexample", negative_price.get("status") == "error", "status=error for price -100", f"status={negative_price.get('status')}, final_price={negative_price.get('final_price')}"))

    precision = candidate_func(99.99, 12.5)
    tests.append(_record("final_price_precision_counterexample", precision.get("status") == "ok" and _close(precision.get("final_price"), 87.49125), "status=ok, final_price=87.49125", f"status={precision.get('status')}, final_price={precision.get('final_price')}"))

    never_negative = candidate_func(10.0, 101.0)
    tests.append(_record("final_price_never_negative_counterexample", never_negative.get("status") == "error", "status=error instead of negative final price", f"status={never_negative.get('status')}, final_price={never_negative.get('final_price')}"))
    return _summarize(tests)
