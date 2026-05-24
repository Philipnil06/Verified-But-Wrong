def _base_order() -> dict:
    return {
        "order_id": "ord_123",
        "original_payment": 100.0,
        "refunded_total": 0.0,
        "status": "paid",
    }


def _record(name: str, passed: bool, expected: str, actual: str) -> dict:
    return {
        "name": name,
        "passed": bool(passed),
        "expected": expected,
        "actual": actual,
    }


def _summarize(tests: list[dict]) -> dict:
    failures = [
        f"{test['name']}: expected {test['expected']}, got {test['actual']}"
        for test in tests
        if not test["passed"]
    ]
    return {
        "passed": len(failures) == 0,
        "passed_count": len(tests) - len(failures),
        "failed_count": len(failures),
        "failures": failures,
        "tests": tests,
    }


def run_tests(refund_func) -> dict:
    tests = []

    negative_result = refund_func(_base_order(), 0)
    tests.append(
        _record(
            "non_positive_amount_rejected",
            negative_result.get("status") == "error",
            "status=error",
            f"status={negative_result.get('status')}",
        )
    )

    valid_result = refund_func(_base_order(), 25.0)
    tests.append(
        _record(
            "positive_amount_on_paid_order_accepted",
            valid_result.get("status") == "ok",
            "status=ok",
            f"status={valid_result.get('status')}",
        )
    )

    return _summarize(tests)
