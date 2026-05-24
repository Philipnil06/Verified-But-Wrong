def _base_order(status: str = "paid") -> dict:
    return {
        "order_id": "ord_123",
        "original_payment": 100.0,
        "refunded_total": 0.0,
        "status": status,
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

    non_positive = refund_func(_base_order(), 0)
    tests.append(
        _record(
            "non_positive_amount_rejected",
            non_positive.get("status") == "error",
            "status=error",
            f"status={non_positive.get('status')}",
        )
    )

    valid = refund_func(_base_order(), 25.0)
    tests.append(
        _record(
            "valid_refund_accepted",
            valid.get("status") == "ok",
            "status=ok",
            f"status={valid.get('status')}",
        )
    )

    order = _base_order()
    first = refund_func(order, 60.0)
    second = refund_func(first.get("order", order), 60.0)
    tests.append(
        _record(
            "double_refund_over_original_payment_rejected",
            first.get("status") == "ok" and second.get("status") == "error",
            "first status=ok, second status=error",
            f"first status={first.get('status')}, second status={second.get('status')}",
        )
    )

    over_refund = refund_func(_base_order(), 150.0)
    tests.append(
        _record(
            "refund_amount_over_original_payment_rejected",
            over_refund.get("status") == "error",
            "status=error",
            f"status={over_refund.get('status')}",
        )
    )

    cancelled = refund_func(_base_order(status="cancelled"), 10.0)
    tests.append(
        _record(
            "cancelled_order_rejected",
            cancelled.get("status") == "error",
            "status=error",
            f"status={cancelled.get('status')}",
        )
    )

    state_update = refund_func(_base_order(), 40.0)
    updated_order = state_update.get("order") or {}
    tests.append(
        _record(
            "refunded_total_updated_after_success",
            state_update.get("status") == "ok"
            and updated_order.get("refunded_total") == 40.0,
            "status=ok, refunded_total=40.0",
            f"status={state_update.get('status')}, refunded_total={updated_order.get('refunded_total')}",
        )
    )

    return _summarize(tests)
