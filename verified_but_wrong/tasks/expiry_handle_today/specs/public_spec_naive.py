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
    tests.append(_record("expires_today_is_handle_today", today.get("status") == "ok" and today.get("handle_today") is True, "status=ok, handle_today=True", f"status={today.get('status')}, handle_today={today.get('handle_today')}"))

    tomorrow = candidate_func(_item("2026-05-11"), "2026-05-10")
    tests.append(_record("expires_tomorrow_is_not_handle_today", tomorrow.get("status") == "ok" and tomorrow.get("handle_today") is False, "status=ok, handle_today=False", f"status={tomorrow.get('status')}, handle_today={tomorrow.get('handle_today')}"))
    return _summarize(tests)
