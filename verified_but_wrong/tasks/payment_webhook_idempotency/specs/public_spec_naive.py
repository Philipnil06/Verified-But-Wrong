def _state() -> dict:
    return {"balances": {"merchant_1": 1000.0}, "processed_event_ids": [], "failed_events": []}


def _event(status: str = "succeeded", event_id: str = "evt_123", amount: float = 500.0, currency: str = "SEK") -> dict:
    return {"event_id": event_id, "merchant_id": "merchant_1", "amount": amount, "currency": currency, "status": status}


def _record(name: str, passed: bool, expected: str, actual: str) -> dict:
    return {"name": name, "passed": bool(passed), "expected": expected, "actual": actual}


def _summarize(tests: list[dict]) -> dict:
    failures = [f"{test['name']}: expected {test['expected']}, got {test['actual']}" for test in tests if not test["passed"]]
    return {"passed": not failures, "passed_count": len(tests) - len(failures), "failed_count": len(failures), "failures": failures, "tests": tests}


def run_tests(candidate_func) -> dict:
    tests = []
    success = candidate_func(_state(), _event(status="succeeded"))
    success_balance = (success.get("state") or {}).get("balances", {}).get("merchant_1")
    tests.append(_record("successful_payment_increases_balance", success.get("status") == "ok" and success_balance == 1500.0, "status=ok, balance=1500.0", f"status={success.get('status')}, balance={success_balance}"))

    failed = candidate_func(_state(), _event(status="failed"))
    failed_balance = (failed.get("state") or {}).get("balances", {}).get("merchant_1")
    tests.append(_record("failed_payment_does_not_increase_balance", failed_balance == 1000.0, "balance=1000.0", f"status={failed.get('status')}, balance={failed_balance}"))
    return _summarize(tests)
