def _order(status: str = "paid", refunded_total: float = 0.0) -> dict:
    return {"order_id": "ord_123", "original_payment": 1000.0, "refunded_total": refunded_total, "status": status, "loyalty_points_awarded": 100}


def _customer(points: int = 100) -> dict:
    return {"customer_id": "cust_1", "loyalty_points": points}


def _record(name: str, passed: bool, expected: str, actual: str) -> dict:
    return {"name": name, "passed": bool(passed), "expected": expected, "actual": actual}


def _summarize(tests: list[dict]) -> dict:
    failures = [f"{t['name']}: expected {t['expected']}, got {t['actual']}" for t in tests if not t["passed"]]
    return {"passed": not failures, "passed_count": len(tests) - len(failures), "failed_count": len(failures), "failures": failures, "tests": tests}


def run_tests(candidate_func) -> dict:
    tests = []
    result = candidate_func(_order(), _customer(), 250.0)
    order = result.get("order") or {}
    tests.append(_record("valid_refund_succeeds", result.get("status") == "ok", "status=ok", f"status={result.get('status')}"))
    tests.append(_record("refunded_total_updates", order.get("refunded_total") == 250.0, "refunded_total=250.0", f"refunded_total={order.get('refunded_total')}"))
    return _summarize(tests)
