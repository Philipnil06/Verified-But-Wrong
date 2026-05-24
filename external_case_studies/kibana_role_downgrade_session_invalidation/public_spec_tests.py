from __future__ import annotations


def make_state() -> dict:
    return {
        "users": {"user_1": {"role": "admin"}},
        "sessions": {
            "session_1": {
                "user_id": "user_1",
                "claims": {"role": "admin"},
                "active": True,
            }
        },
        "audit": [],
    }


def _test(name: str, passed: bool, expected: str, actual: str) -> dict:
    return {"name": name, "passed": passed, "expected": expected, "actual": actual}


def run_tests(candidate_module) -> dict:
    tests = []

    state = make_state()
    result = candidate_module.update_role(state, "user_1", "none")
    updated = result.get("state", {})
    tests.append(
        _test(
            "admin_can_change_role_from_admin_to_none",
            result.get("status") == "ok",
            "status ok",
            str(result.get("status")),
        )
    )
    tests.append(
        _test(
            "stored_role_is_updated",
            updated.get("users", {}).get("user_1", {}).get("role") == "none",
            "stored role none",
            str(updated.get("users", {}).get("user_1", {}).get("role")),
        )
    )
    view = candidate_module.view_user(updated, "user_1")
    tests.append(
        _test(
            "refreshed_view_shows_updated_role",
            view.get("status") == "ok" and view.get("user", {}).get("role") == "none",
            "view role none",
            str(view.get("user")),
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
