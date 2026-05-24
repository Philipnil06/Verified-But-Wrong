def allow_request(state: dict, user_id: str, timestamp: int) -> dict:
    return {"allowed": False, "message": "Blocked.", "state": state or {}}
