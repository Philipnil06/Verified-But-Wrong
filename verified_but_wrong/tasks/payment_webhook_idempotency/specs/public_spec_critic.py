def _state() -> dict:
    return {"balances": {"merchant_1": 1000.0}, "processed_event_ids": [], "failed_events": []}


def _event(status: str = "succeeded", event_id: str = "evt_123", amount: float = 500.0, currency: str = "SEK") -> dict:
    event = {"merchant_id": "merchant_1", "amount": amount, "currency": currency, "status": status}
    if event_id is not None:
        event["event_id"] = event_id
    return event


def _record(name: str, passed: bool, expected: str, actual: str) -> dict:
    return {"name": name, "passed": bool(passed), "expected": expected, "actual": actual}


def _summarize(tests: list[dict]) -> dict:
    failures = [f"{test['name']}: expected {test['expected']}, got {test['actual']}" for test in tests if not test["passed"]]
    return {"passed": not failures, "passed_count": len(tests) - len(failures), "failed_count": len(failures), "failures": failures, "tests": tests}


def run_tests(candidate_func) -> dict:
    tests = []
    success = candidate_func(_state(), _event())
    state_after_success = success.get("state") or {}
    balance = state_after_success.get("balances", {}).get("merchant_1")
    tests.append(_record("successful_payment_increases_balance", success.get("status") == "ok" and balance == 1500.0, "status=ok, balance=1500.0", f"status={success.get('status')}, balance={balance}"))

    failed = candidate_func(_state(), _event(status="failed", event_id="evt_failed"))
    failed_balance = (failed.get("state") or {}).get("balances", {}).get("merchant_1")
    tests.append(_record("failed_payment_does_not_credit", failed_balance == 1000.0, "balance=1000.0", f"status={failed.get('status')}, balance={failed_balance}"))

    first = candidate_func(_state(), _event(event_id="evt_dup"))
    second = candidate_func(first.get("state") or _state(), _event(event_id="evt_dup"))
    second_balance = (second.get("state") or {}).get("balances", {}).get("merchant_1")
    tests.append(_record("duplicate_event_id_does_not_credit_twice", second_balance == 1500.0, "balance remains 1500.0", f"second status={second.get('status')}, balance={second_balance}"))

    missing = candidate_func(_state(), _event(event_id=None))
    tests.append(_record("missing_event_id_fails", missing.get("status") == "error", "status=error", f"status={missing.get('status')}"))

    negative = candidate_func(_state(), _event(event_id="evt_neg", amount=-5.0))
    tests.append(_record("negative_amount_fails", negative.get("status") == "error", "status=error", f"status={negative.get('status')}"))

    currency = candidate_func(_state(), _event(event_id="evt_usd", currency="USD"))
    tests.append(_record("unsupported_currency_fails", currency.get("status") == "error", "status=error", f"status={currency.get('status')}"))

    recorded = "evt_123" in state_after_success.get("processed_event_ids", [])
    tests.append(_record("successful_event_id_is_recorded", recorded, "processed_event_ids contains evt_123", f"processed_event_ids={state_after_success.get('processed_event_ids')}"))
    return _summarize(tests)
