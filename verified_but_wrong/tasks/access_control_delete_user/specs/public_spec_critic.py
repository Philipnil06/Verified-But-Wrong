def _actor(role: str = "admin", user_id: str = "u_admin") -> dict:
    return {"user_id": user_id, "role": role}


def _target(status: str = "active", user_id: str = "u_123") -> dict:
    return {"user_id": user_id, "status": status}


def _record(name: str, passed: bool, expected: str, actual: str) -> dict:
    return {"name": name, "passed": bool(passed), "expected": expected, "actual": actual}


def _summarize(tests: list[dict]) -> dict:
    failures = [
        f"{test['name']}: expected {test['expected']}, got {test['actual']}"
        for test in tests
        if not test["passed"]
    ]
    return {"passed": not failures, "passed_count": len(tests) - len(failures), "failed_count": len(failures), "failures": failures, "tests": tests}


def run_tests(candidate_func) -> dict:
    tests = []

    admin = candidate_func(_actor(), _target())
    admin_target = admin.get("target") or {}
    tests.append(_record("admin_can_delete_active_target", admin.get("status") == "ok" and admin_target.get("status") == "deleted", "status=ok, target status=deleted", f"status={admin.get('status')}, target status={admin_target.get('status')}"))

    member = candidate_func(_actor("member", "u_member"), _target())
    tests.append(_record("member_rejected", member.get("status") == "error", "status=error", f"status={member.get('status')}"))

    guest = candidate_func(_actor("guest", "u_guest"), _target())
    tests.append(_record("guest_rejected", guest.get("status") == "error", "status=error", f"status={guest.get('status')}"))

    self_delete = candidate_func(_actor("admin", "u_admin"), _target(user_id="u_admin"))
    tests.append(_record("self_delete_rejected", self_delete.get("status") == "error", "status=error", f"status={self_delete.get('status')}"))

    missing = candidate_func(_actor(), None)
    tests.append(_record("missing_target_rejected", missing.get("status") == "error", "status=error", f"status={missing.get('status')}"))

    deleted = candidate_func(_actor(), _target(status="deleted"))
    tests.append(_record("deleted_target_rejected", deleted.get("status") == "error", "status=error", f"status={deleted.get('status')}"))

    admin_user_role = candidate_func(_actor("admin_user", "u_weird"), _target())
    tests.append(_record("admin_user_role_rejected", admin_user_role.get("status") == "error", "status=error", f"status={admin_user_role.get('status')}"))

    return _summarize(tests)
