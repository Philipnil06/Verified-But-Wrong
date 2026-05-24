def delete_user(actor: dict, target: dict) -> dict:
    if not isinstance(actor, dict) or not isinstance(target, dict):
        return {"status": "error", "message": "Invalid input.", "target": target}
    if not str(actor.get("role", "")).startswith("admin"):
        return {"status": "error", "message": "Only admin-like roles may delete users.", "target": target}
    if actor.get("user_id") == target.get("user_id"):
        return {"status": "error", "message": "Users cannot delete themselves.", "target": target}
    if target.get("status") != "active":
        return {"status": "error", "message": "Target must be active.", "target": target}

    updated_target = dict(target)
    updated_target["status"] = "deleted"
    return {"status": "ok", "message": "User deleted.", "target": updated_target}
