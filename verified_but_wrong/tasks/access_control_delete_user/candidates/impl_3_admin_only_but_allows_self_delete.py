def delete_user(actor: dict, target: dict) -> dict:
    if not isinstance(actor, dict) or not isinstance(target, dict):
        return {"status": "error", "message": "Invalid input.", "target": target}
    if actor.get("role") != "admin":
        return {"status": "error", "message": "Only admins may delete users.", "target": target}
    if target.get("status") != "active":
        return {"status": "error", "message": "Target must be active.", "target": target}

    updated_target = dict(target)
    updated_target["status"] = "deleted"
    return {"status": "ok", "message": "User deleted.", "target": updated_target}
