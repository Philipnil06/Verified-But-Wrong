def delete_user(actor: dict, target: dict) -> dict:
    if not isinstance(target, dict):
        return {"status": "error", "message": "Target is invalid.", "target": target}

    updated_target = dict(target)
    updated_target["status"] = "deleted"
    return {"status": "ok", "message": "User deleted.", "target": updated_target}
