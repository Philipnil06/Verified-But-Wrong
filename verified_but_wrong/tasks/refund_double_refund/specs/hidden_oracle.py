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

    non_positive = refund_func(_base_order(), -1.0)
    tests.append(
        _record(
            "non_positive_amount_rejected",
            non_positive.get("status") == "error",
            "status=error",
            f"status={non_positive.get('status')}",
        )
    )

    valid = refund_func(_base_order(), 25.0)
    valid_order = valid.get("order") or {}
    tests.append(
        _record(
            "valid_refund_succeeds_and_updates_state",
            valid.get("status") == "ok" and valid_order.get("refunded_total") == 25.0,
            "status=ok, refunded_total=25.0",
            f"status={valid.get('status')}, refunded_total={valid_order.get('refunded_total')}",
        )
    )

    order = _base_order()
    first = refund_func(order, 60.0)
    second = refund_func(first.get("order", order), 60.0)
    tests.append(
        _record(
            "double_refund_counterexample",
            first.get("status") == "ok" and second.get("status") == "error",
            "first refund 60 status=ok, second refund 60 status=error",
            f"first status={first.get('status')}, second status={second.get('status')}",
        )
    )

    over_refund = refund_func(_base_order(), 150.0)
    tests.append(
        _record(
            "over_refund_counterexample",
            over_refund.get("status") == "error",
            "status=error for refund 150 on original_payment 100",
            f"status={over_refund.get('status')}",
        )
    )

    cancelled = refund_func(_base_order(status="cancelled"), 10.0)
    tests.append(
        _record(
            "cancelled_order_counterexample",
            cancelled.get("status") == "error",
            "status=error for cancelled order",
            f"status={cancelled.get('status')}",
        )
    )

    state_update = refund_func(_base_order(), 40.0)
    state_order = state_update.get("order") or {}
    tests.append(
        _record(
            "state_update_counterexample",
            state_update.get("status") == "ok" and state_order.get("refunded_total") == 40.0,
            "after refund 40, refunded_total=40.0",
            f"status={state_update.get('status')}, refunded_total={state_order.get('refunded_total')}",
        )
    )

    full_refund = refund_func(_base_order(), 100.0)
    full_order = full_refund.get("order") or {}
    tests.append(
        _record(
            "full_refund_marks_order_refunded",
            full_refund.get("status") == "ok"
            and full_order.get("refunded_total") == 100.0
            and full_order.get("status") == "refunded",
            "status=ok, refunded_total=100.0, order status=refunded",
            f"status={full_refund.get('status')}, refunded_total={full_order.get('refunded_total')}, order status={full_order.get('status')}",
        )
    )

    invalid_order = refund_func(None, 10.0)
    tests.append(
        _record(
            "invalid_order_rejected",
            invalid_order.get("status") == "error",
            "status=error for invalid order",
            f"status={invalid_order.get('status')}",
        )
    )

    return _summarize(tests)
