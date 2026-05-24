def allow_request(state: dict, user_id: str, timestamp: int) -> dict:
    updated_state = {key: list(value) for key, value in (state or {}).items()}
    recent = [old for old in updated_state.get(user_id, []) if timestamp - old < 60]

    if len(recent) >= 5:
        updated_state[user_id] = recent
        return {"allowed": False, "message": "Rate limit exceeded.", "state": updated_state}

    recent.append(timestamp)
    updated_state[user_id] = recent
    return {"allowed": True, "message": "Allowed.", "state": updated_state}
