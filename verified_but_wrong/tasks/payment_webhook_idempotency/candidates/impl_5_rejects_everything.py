def process_payment_event(state: dict, event: dict) -> dict:
    return {"status": "error", "message": "Payment event rejected.", "state": state or {}}
