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


def _summarize(tests: list[dict]) -> dict:
    failures = [f"{test['name']}: expected {test['expected']}, got {test['actual']}" for test in tests if not test["passed"]]
    return {"passed": not failures, "passed_count": len(tests) - len(failures), "failed_count": len(failures), "failures": failures, "tests": tests}


def run_tests(candidate_func) -> dict:
    tests = []
    valid = candidate_func(_order(), 100.0, "2026-04-10")
    valid_order = valid.get("order") or {}
    tests.append(_record("valid_refund_works", valid.get("status") == "ok", "status=ok", f"status={valid.get('status')}"))

    over = candidate_func(_order(refunded_total=950.0), 100.0, "2026-04-10")
    tests.append(_record("amount_cannot_exceed_remaining_paid_amount", over.get("status") == "error", "status=error", f"status={over.get('status')}"))

    tests.append(_record("refunded_total_updates", valid_order.get("refunded_total") == 100.0, "refunded_total=100.0", f"refunded_total={valid_order.get('refunded_total')}"))

    day30 = candidate_func(_order(), 100.0, "2026-05-01")
    tests.append(_record("day_30_is_allowed", day30.get("status") == "ok", "status=ok", f"status={day30.get('status')}"))

    day31 = candidate_func(_order(), 100.0, "2026-05-02")
    tests.append(_record("day_31_without_override_rejected", day31.get("status") == "error", "status=error", f"status={day31.get('status')}"))

    override = candidate_func(_order(manual_override=True), 100.0, "2026-05-10")
    tests.append(_record("manual_override_allows_after_day_30", override.get("status") == "ok", "status=ok", f"status={override.get('status')}"))

    cancelled = candidate_func(_order(status="cancelled"), 100.0, "2026-04-10")
    tests.append(_record("cancelled_order_fails", cancelled.get("status") == "error", "status=error", f"status={cancelled.get('status')}"))

    chargeback = candidate_func(_order(status="chargeback"), 100.0, "2026-04-10")
    tests.append(_record("chargeback_order_fails", chargeback.get("status") == "error", "status=error", f"status={chargeback.get('status')}"))
    return _summarize(tests)
