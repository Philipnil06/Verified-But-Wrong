def _order(status: str = "paid") -> dict:
    return {"order_id": "ord_123", "original_payment": 100.0, "refunded_total": 0.0, "status": status}


def _record(name: str, passed: bool, expected: str, actual: str) -> dict:
    return {"name": name, "passed": bool(passed), "expected": expected, "actual": actual}


def valid_refund_succeeds(candidate_func) -> dict:
    result = candidate_func(_order(), 25.0)
    return _record("valid_refund_succeeds", result.get("status") == "ok", "status=ok", f"status={result.get('status')}")


def no_over_refund(candidate_func) -> dict:
    result = candidate_func(_order(), 150.0)
    return _record("refund_must_not_exceed_original_payment", result.get("status") == "error", "status=error", f"status={result.get('status')}")


def no_double_refund(candidate_func) -> dict:
    first = candidate_func(_order(), 60.0)
    second = candidate_func(first.get("order", _order()), 60.0)
    passed = first.get("status") == "ok" and second.get("status") == "error"
    actual = f"first status={first.get('status')}, second status={second.get('status')}"
    return _record("same_order_cannot_be_refunded_twice", passed, "first status=ok, second status=error", actual)


def cancelled_orders_fail(candidate_func) -> dict:
    result = candidate_func(_order(status="cancelled"), 10.0)
    return _record("invalid_or_cancelled_orders_fail", result.get("status") == "error", "status=error", f"status={result.get('status')}")


def state_updates_after_success(candidate_func) -> dict:
    result = candidate_func(_order(), 40.0)
    updated = result.get("order") or {}
    passed = result.get("status") == "ok" and updated.get("refunded_total") == 40.0
    actual = f"status={result.get('status')}, refunded_total={updated.get('refunded_total')}"
    return _record("refunded_state_updated_after_success", passed, "status=ok, refunded_total=40.0", actual)


REQUIREMENT_TESTS = {
    "Valid positive refund on paid order succeeds": valid_refund_succeeds,
    "Refund must not exceed original payment": no_over_refund,
    "Same order cannot be refunded twice": no_double_refund,
    "Invalid or cancelled orders must fail": cancelled_orders_fail,
    "Refunded state must be updated after successful refund": state_updates_after_success,
}
