def _state() -> dict:
    return {"balances": {"merchant_1": 1000.0}, "processed_event_ids": [], "failed_events": []}


def _event(status: str = "succeeded", event_id: str = "evt_123", amount: float = 500.0, currency: str = "SEK") -> dict:
    event = {"merchant_id": "merchant_1", "amount": amount, "currency": currency, "status": status}
    if event_id is not None:
        event["event_id"] = event_id
    return event


def _record(name: str, passed: bool, expected: str, actual: str) -> dict:
    return {"name": name, "passed": bool(passed), "expected": expected, "actual": actual}


def successful_payment_credits(candidate_func) -> dict:
    result = candidate_func(_state(), _event())
    balance = (result.get("state") or {}).get("balances", {}).get("merchant_1")
    return _record("successful_payment_events_increase_balance", result.get("status") == "ok" and balance == 1500.0, "status=ok, balance=1500.0", f"status={result.get('status')}, balance={balance}")


def failed_payment_no_credit(candidate_func) -> dict:
    result = candidate_func(_state(), _event(status="failed", event_id="evt_failed"))
    balance = (result.get("state") or {}).get("balances", {}).get("merchant_1")
    return _record("failed_payments_must_not_credit_balance", balance == 1000.0, "balance=1000.0", f"status={result.get('status')}, balance={balance}")


def duplicate_event_no_double_credit(candidate_func) -> dict:
    first = candidate_func(_state(), _event(event_id="evt_dup"))
    second = candidate_func(first.get("state") or _state(), _event(event_id="evt_dup"))
    balance = (second.get("state") or {}).get("balances", {}).get("merchant_1")
    return _record("same_event_id_not_credited_twice", balance == 1500.0, "balance remains 1500.0", f"second status={second.get('status')}, balance={balance}")


def missing_event_id_fails(candidate_func) -> dict:
    result = candidate_func(_state(), _event(event_id=None))
    return _record("missing_event_id_must_fail", result.get("status") == "error", "status=error", f"status={result.get('status')}")


def amount_positive(candidate_func) -> dict:
    result = candidate_func(_state(), _event(event_id="evt_neg", amount=-5.0))
    return _record("amount_must_be_positive", result.get("status") == "error", "status=error", f"status={result.get('status')}")


def unsupported_currency_fails(candidate_func) -> dict:
    result = candidate_func(_state(), _event(event_id="evt_usd", currency="USD"))
    return _record("unsupported_currency_must_fail", result.get("status") == "error", "status=error", f"status={result.get('status')}")


def processed_event_id_recorded(candidate_func) -> dict:
    result = candidate_func(_state(), _event(event_id="evt_recorded"))
    processed = (result.get("state") or {}).get("processed_event_ids", [])
    return _record("processed_successful_event_ids_recorded", "evt_recorded" in processed, "processed_event_ids contains evt_recorded", f"processed_event_ids={processed}")


REQUIREMENT_TESTS = {
    "Successful payment events should increase merchant balance": successful_payment_credits,
    "Failed payment events should not increase balance": failed_payment_no_credit,
    "The same event_id must not be credited twice": duplicate_event_no_double_credit,
    "Missing event_id must fail": missing_event_id_fails,
    "Amount must be positive": amount_positive,
    "Unsupported currency must fail": unsupported_currency_fails,
    "Failed payments must not credit balance": failed_payment_no_credit,
    "Processed successful event IDs must be recorded": processed_event_id_recorded,
}
