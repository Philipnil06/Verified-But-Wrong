def _actor(role: str = "admin", user_id: str = "u_admin") -> dict:
    return {"user_id": user_id, "role": role}


def _target(status: str = "active", user_id: str = "u_123") -> dict:
    return {"user_id": user_id, "status": status}


def _record(name: str, passed: bool, expected: str, actual: str) -> dict:
    return {"name": name, "passed": bool(passed), "expected": expected, "actual": actual}


def admin_delete_succeeds(candidate_func) -> dict:
    result = candidate_func(_actor(), _target())
    target = result.get("target") or {}
    passed = result.get("status") == "ok" and target.get("status") == "deleted"
    actual = f"status={result.get('status')}, target status={target.get('status')}"
    return _record("admin_can_delete_active_target", passed, "status=ok, target status=deleted", actual)


def only_admins(candidate_func) -> dict:
    result = candidate_func(_actor(role="member", user_id="u_member"), _target())
    return _record("only_admins_may_delete_users", result.get("status") == "error", "status=error", f"status={result.get('status')}")


def members_and_guests_rejected(candidate_func) -> dict:
    member = candidate_func(_actor(role="member", user_id="u_member"), _target())
    guest = candidate_func(_actor(role="guest", user_id="u_guest"), _target())
    passed = member.get("status") == "error" and guest.get("status") == "error"
    actual = f"member status={member.get('status')}, guest status={guest.get('status')}"
    return _record("members_and_guests_rejected", passed, "member status=error, guest status=error", actual)


def self_delete_rejected(candidate_func) -> dict:
    result = candidate_func(_actor(user_id="u_admin"), _target(user_id="u_admin"))
    return _record("users_cannot_delete_themselves", result.get("status") == "error", "status=error", f"status={result.get('status')}")


def missing_target_fails(candidate_func) -> dict:
    result = candidate_func(_actor(), None)
    return _record("missing_target_users_fail", result.get("status") == "error", "status=error", f"status={result.get('status')}")


def deleted_state_updated(candidate_func) -> dict:
    result = candidate_func(_actor(), _target())
    target = result.get("target") or {}
    passed = result.get("status") == "ok" and target.get("status") == "deleted"
    actual = f"status={result.get('status')}, target status={target.get('status')}"
    return _record("deleted_state_updated", passed, "status=ok, target status=deleted", actual)


REQUIREMENT_TESTS = {
    "Admin can delete active target": admin_delete_succeeds,
    "Only admins may delete users": only_admins,
    "Members and guests must be rejected": members_and_guests_rejected,
    "Users cannot delete themselves": self_delete_rejected,
    "Missing target users must fail": missing_target_fails,
    "Deleted state must be updated": deleted_state_updated,
}
