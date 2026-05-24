def _order(status: str = "paid", refunded_total: float = 0.0, manual_override: bool = False) -> dict:
    return {
        "order_id": "ord_123",
        "purchase_date": "2026-04-01",
        "original_payment": 1000.0,
        "refunded_total": refunded_total,
        "status": status,
        "manual_override": manual_override,
    }


def _record(name: str, passed: bool, expected: str, actual: str) -> dict:
    return {"name": name, "passed": bool(passed), "expected": expected, "actual": actual}


def valid_paid_order_refund_succeeds(candidate_func) -> dict:
    result = candidate_func(_order(), 100.0, "2026-04-10")
    return _record("valid_paid_order_refund_succeeds", result.get("status") == "ok", "status=ok", f"status={result.get('status')}")


def refund_cannot_exceed_remaining(candidate_func) -> dict:
    result = candidate_func(_order(refunded_total=950.0), 100.0, "2026-04-10")
    return _record("refund_cannot_exceed_remaining_paid_amount", result.get("status") == "error", "status=error", f"status={result.get('status')}")


def successful_refunds_update_total(candidate_func) -> dict:
    result = candidate_func(_order(), 100.0, "2026-04-10")
    updated = result.get("order") or {}
    return _record("successful_refunds_update_refunded_total", updated.get("refunded_total") == 100.0, "refunded_total=100.0", f"refunded_total={updated.get('refunded_total')}")


def refund_window_enforced(candidate_func) -> dict:
    result = candidate_func(_order(), 100.0, "2026-05-02")
    return _record("refunds_only_allowed_within_30_days_unless_override", result.get("status") == "error", "status=error on day 31 without override", f"status={result.get('status')}")


def day_30_allowed_day_31_rejected(candidate_func) -> dict:
    day30 = candidate_func(_order(), 100.0, "2026-05-01")
    day31 = candidate_func(_order(), 100.0, "2026-05-02")
    passed = day30.get("status") == "ok" and day31.get("status") == "error"
    actual = f"day30 status={day30.get('status')}, day31 status={day31.get('status')}"
    return _record("day_30_allowed_day_31_rejected", passed, "day30 status=ok, day31 status=error", actual)


def manual_override_allows_late_refund(candidate_func) -> dict:
    result = candidate_func(_order(manual_override=True), 100.0, "2026-05-10")
    return _record("manual_override_permits_refunds_after_normal_window", result.get("status") == "ok", "status=ok", f"status={result.get('status')}")


def cancelled_or_chargeback_fail(candidate_func) -> dict:
    cancelled = candidate_func(_order(status="cancelled"), 100.0, "2026-04-10")
    chargeback = candidate_func(_order(status="chargeback"), 100.0, "2026-04-10")
    passed = cancelled.get("status") == "error" and chargeback.get("status") == "error"
    actual = f"cancelled status={cancelled.get('status')}, chargeback status={chargeback.get('status')}"
    return _record("cancelled_or_chargeback_orders_cannot_be_refunded", passed, "both statuses=error", actual)


REQUIREMENT_TESTS = {
    "Valid paid order refund succeeds": valid_paid_order_refund_succeeds,
    "Refund cannot exceed remaining paid amount": refund_cannot_exceed_remaining,
    "Successful refunds must update refunded_total": successful_refunds_update_total,
    "Refunds are only allowed within 30 days of purchase unless manual_override is true": refund_window_enforced,
    "Day 30 is still allowed but day 31 is rejected without manual_override": day_30_allowed_day_31_rejected,
    "Manual override permits refunds after the normal window": manual_override_allows_late_refund,
    "Cancelled or chargeback orders cannot be refunded": cancelled_or_chargeback_fail,
}
