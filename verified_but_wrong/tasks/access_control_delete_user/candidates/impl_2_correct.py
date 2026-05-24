def delete_user(actor: dict, target: dict) -> dict:
    if not isinstance(actor, dict):
        return {"status": "error", "message": "Actor is invalid.", "target": target}
    if not isinstance(target, dict):
        return {"status": "error", "message": "Target is invalid.", "target": target}
    if actor.get("role") != "admin":
        return {"status": "error", "message": "Only admins may delete users.", "target": target}
    if actor.get("user_id") == target.get("user_id"):
        return {"status": "error", "message": "Users cannot delete themselves.", "target": target}
    if target.get("status") != "active":
        return {"status": "error", "message": "Target must be active.", "target": target}

    updated_target = dict(target)
    updated_target["status"] = "deleted"
    return {"status": "ok", "message": "User deleted.", "target": updated_target}
