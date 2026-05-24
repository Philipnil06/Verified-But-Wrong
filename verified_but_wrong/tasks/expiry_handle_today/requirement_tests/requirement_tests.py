def _item(expiry_date: str, lead_time: int = 0) -> dict:
    return {"name": "Milk", "expiry_date": expiry_date, "category_lead_time_days": lead_time}


def _record(name: str, passed: bool, expected: str, actual: str) -> dict:
    return {"name": name, "passed": bool(passed), "expected": expected, "actual": actual}


def expires_today_true(candidate_func) -> dict:
    result = candidate_func(_item("2026-05-10"), "2026-05-10")
    passed = result.get("status") == "ok" and result.get("handle_today") is True
    actual = f"status={result.get('status')}, handle_today={result.get('handle_today')}"
    return _record("expires_today_handle_today_true", passed, "status=ok, handle_today=True", actual)


def lead_time_applied(candidate_func) -> dict:
    result = candidate_func(_item("2026-05-12", 3), "2026-05-10")
    passed = result.get("status") == "ok" and result.get("handle_today") is True
    actual = f"status={result.get('status')}, handle_today={result.get('handle_today')}"
    return _record("category_lead_time_applied", passed, "status=ok, handle_today=True", actual)


def earlier_items_still_handled(candidate_func) -> dict:
    result = candidate_func(_item("2026-05-11", 3), "2026-05-10")
    passed = result.get("status") == "ok" and result.get("handle_today") is True
    actual = f"status={result.get('status')}, handle_today={result.get('handle_today')}"
    return _record("items_that_should_have_been_handled_earlier_are_still_handled", passed, "status=ok, handle_today=True", actual)


def expired_items_handled(candidate_func) -> dict:
    result = candidate_func(_item("2026-05-09"), "2026-05-10")
    passed = result.get("status") == "ok" and result.get("handle_today") is True
    actual = f"status={result.get('status')}, handle_today={result.get('handle_today')}"
    return _record("already_expired_items_must_be_handled", passed, "status=ok, handle_today=True", actual)


def invalid_date_fails(candidate_func) -> dict:
    result = candidate_func(_item("not-a-date"), "2026-05-10")
    return _record("invalid_date_input_must_fail", result.get("status") == "error", "status=error", f"status={result.get('status')}")


def today_or_earlier_boundary(candidate_func) -> dict:
    result = candidate_func(_item("2026-05-13", 3), "2026-05-10")
    passed = result.get("status") == "ok" and result.get("handle_today") is True
    actual = f"status={result.get('status')}, handle_today={result.get('handle_today')}"
    return _record("boundary_uses_today_or_earlier", passed, "status=ok, handle_today=True", actual)


REQUIREMENT_TESTS = {
    "Item expiring today is handle_today": expires_today_true,
    "Category lead time must be applied": lead_time_applied,
    "Items that should have been handled earlier are still handle_today": earlier_items_still_handled,
    "Already expired items must be handled": expired_items_handled,
    "Invalid date input must fail": invalid_date_fails,
    "Boundary condition uses today or earlier, not only exact equality": today_or_earlier_boundary,
}
