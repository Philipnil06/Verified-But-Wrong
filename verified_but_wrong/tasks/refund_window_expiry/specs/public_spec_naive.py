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
    tests.append(_record("valid_paid_order_refund_succeeds", valid.get("status") == "ok", "status=ok", f"status={valid.get('status')}"))

    over = candidate_func(_order(refunded_total=950.0), 100.0, "2026-04-10")
    tests.append(_record("amount_cannot_exceed_remaining_paid_amount", over.get("status") == "error", "status=error", f"status={over.get('status')}"))

    tests.append(_record("refunded_total_updates_after_success", valid_order.get("refunded_total") == 100.0, "refunded_total=100.0", f"refunded_total={valid_order.get('refunded_total')}"))
    return _summarize(tests)
