from __future__ import annotations

from copy import deepcopy


def update_role(state: dict, user_id: str, new_role: str) -> dict:
    updated = deepcopy(state)
    if user_id not in updated.get("users", {}):
        return {"status": "error", "message": "user not found", "state": updated}
    updated["users"][user_id]["role"] = new_role
    return {"status": "ok", "message": "role updated", "state": updated}


def view_user(state: dict, user_id: str) -> dict:
    user = deepcopy(state.get("users", {}).get(user_id))
    if not user:
        return {"status": "error", "message": "user not found", "user": None}
    return {"status": "ok", "message": "user loaded", "user": user}


def perform_admin_action(state: dict, session_id: str) -> dict:
    session = state.get("sessions", {}).get(session_id)
    if not session or not session.get("active", True):
        return {"status": "error", "allowed": False, "message": "admin action denied"}
    user_id = session.get("user_id")
    current_role = state.get("users", {}).get(user_id, {}).get("role")
    if current_role == "admin":
        return {"status": "ok", "allowed": True, "message": "admin action allowed after current-role check"}
    return {"status": "error", "allowed": False, "message": "current stored role is not admin"}
