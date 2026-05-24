def _item(expiry_date: str, lead_time: int = 0) -> dict:
    return {"name": "Milk", "expiry_date": expiry_date, "category_lead_time_days": lead_time}


def _record(name: str, passed: bool, expected: str, actual: str) -> dict:
    return {"name": name, "passed": bool(passed), "expected": expected, "actual": actual}


def _summarize(tests: list[dict]) -> dict:
    failures = [f"{test['name']}: expected {test['expected']}, got {test['actual']}" for test in tests if not test["passed"]]
    return {"passed": not failures, "passed_count": len(tests) - len(failures), "failed_count": len(failures), "failures": failures, "tests": tests}


def run_tests(candidate_func) -> dict:
    tests = []
    today = candidate_func(_item("2026-05-10"), "2026-05-10")
    tests.append(_record("expires_today_true", today.get("status") == "ok" and today.get("handle_today") is True, "status=ok, handle_today=True", f"status={today.get('status')}, handle_today={today.get('handle_today')}"))

    expired = candidate_func(_item("2026-05-09"), "2026-05-10")
    tests.append(_record("expired_yesterday_true", expired.get("status") == "ok" and expired.get("handle_today") is True, "status=ok, handle_today=True", f"status={expired.get('status')}, handle_today={expired.get('handle_today')}"))

    lead_two = candidate_func(_item("2026-05-12", 3), "2026-05-10")
    tests.append(_record("lead_time_makes_future_item_true", lead_two.get("status") == "ok" and lead_two.get("handle_today") is True, "status=ok, handle_today=True", f"status={lead_two.get('status')}, handle_today={lead_two.get('handle_today')}"))

    boundary = candidate_func(_item("2026-05-13", 3), "2026-05-10")
    tests.append(_record("exact_handle_date_boundary_true", boundary.get("status") == "ok" and boundary.get("handle_today") is True, "status=ok, handle_today=True", f"status={boundary.get('status')}, handle_today={boundary.get('handle_today')}"))

    future = candidate_func(_item("2026-05-14", 3), "2026-05-10")
    tests.append(_record("future_outside_lead_time_false", future.get("status") == "ok" and future.get("handle_today") is False, "status=ok, handle_today=False", f"status={future.get('status')}, handle_today={future.get('handle_today')}"))

    invalid = candidate_func(_item("not-a-date", 0), "2026-05-10")
    tests.append(_record("invalid_date_rejected", invalid.get("status") == "error", "status=error", f"status={invalid.get('status')}"))

    negative_lead = candidate_func(_item("2026-05-12", -1), "2026-05-10")
    tests.append(_record("negative_lead_time_rejected", negative_lead.get("status") == "error", "status=error", f"status={negative_lead.get('status')}"))
    return _summarize(tests)
