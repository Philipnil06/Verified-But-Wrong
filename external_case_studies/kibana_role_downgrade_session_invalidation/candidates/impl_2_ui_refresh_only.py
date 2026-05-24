from __future__ import annotations

from copy import deepcopy


def update_role(state: dict, user_id: str, new_role: str) -> dict:
    updated = deepcopy(state)
    if user_id not in updated.get("users", {}):
        return {"status": "error", "message": "user not found", "state": updated}
    updated["users"][user_id]["role"] = new_role
    updated.setdefault("view_cache", {})[user_id] = {"role": new_role}
    return {"status": "ok", "message": "role updated and refresh cache changed", "state": updated}


def view_user(state: dict, user_id: str) -> dict:
    cached = state.get("view_cache", {}).get(user_id)
    if cached:
        return {"status": "ok", "message": "refreshed user loaded", "user": deepcopy(cached)}
    user = deepcopy(state.get("users", {}).get(user_id))
    if not user:
        return {"status": "error", "message": "user not found", "user": None}
    return {"status": "ok", "message": "user loaded", "user": user}


def perform_admin_action(state: dict, session_id: str) -> dict:
    session = state.get("sessions", {}).get(session_id)
    if session and session.get("claims", {}).get("role") == "admin":
        return {"status": "ok", "allowed": True, "message": "backend trusted stale session claims"}
    return {"status": "error", "allowed": False, "message": "admin action denied"}
