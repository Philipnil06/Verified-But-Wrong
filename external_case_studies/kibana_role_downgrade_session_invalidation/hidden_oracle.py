from __future__ import annotations

from public_spec_tests import make_state


def _test(name: str, passed: bool, expected: str, actual: str) -> dict:
    return {"name": name, "passed": passed, "expected": expected, "actual": actual}


def run_tests(candidate_module) -> dict:
    tests = []

    state = make_state()
    downgrade = candidate_module.update_role(state, "user_1", "none")
    updated = downgrade.get("state", {})
    action = candidate_module.perform_admin_action(updated, "session_1")

    tests.append(
        _test(
            "role_downgrade_succeeds",
            downgrade.get("status") == "ok" and updated.get("users", {}).get("user_1", {}).get("role") == "none",
            "role updated to none",
            f"status={downgrade.get('status')} role={updated.get('users', {}).get('user_1', {}).get('role')}",
        )
    )
    tests.append(
        _test(
            "old_admin_session_cannot_perform_privileged_action_after_downgrade",
            action.get("allowed") is False,
            "old session denied after role downgrade",
            f"allowed={action.get('allowed')} message={action.get('message')}",
        )
    )

    failures = [t["name"] for t in tests if not t["passed"]]
    return {
        "passed": not failures,
        "passed_count": len(tests) - len(failures),
        "failed_count": len(failures),
        "failures": failures,
        "tests": tests,
    }
