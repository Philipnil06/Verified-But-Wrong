from __future__ import annotations

from copy import deepcopy


def update_role(state: dict, user_id: str, new_role: str) -> dict:
    updated = deepcopy(state)
    users = updated.get("users", {})
    if user_id not in users:
        return {"status": "error", "message": "user not found", "state": updated}
    old_role = users[user_id].get("role")
    users[user_id]["role"] = new_role
    if old_role == "admin" and new_role != "admin":
        for session in updated.get("sessions", {}).values():
            if session.get("user_id") == user_id:
                session["active"] = False
    return {"status": "ok", "message": "role updated and downgraded sessions invalidated", "state": updated}


def view_user(state: dict, user_id: str) -> dict:
    user = deepcopy(state.get("users", {}).get(user_id))
    if not user:
        return {"status": "error", "message": "user not found", "user": None}
    return {"status": "ok", "message": "user loaded", "user": user}


def perform_admin_action(state: dict, session_id: str) -> dict:
    session = state.get("sessions", {}).get(session_id)
    if session and session.get("active", True) and session.get("claims", {}).get("role") == "admin":
        return {"status": "ok", "allowed": True, "message": "admin action allowed"}
    return {"status": "error", "allowed": False, "message": "session inactive or not admin"}
