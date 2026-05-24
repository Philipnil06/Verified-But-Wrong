def allow_request(state: dict, user_id: str, timestamp: int) -> dict:
    updated_state = {key: list(value) for key, value in (state or {}).items()}
    updated_state.setdefault(user_id, []).append(timestamp)
    return {"allowed": True, "message": "Allowed.", "state": updated_state}
