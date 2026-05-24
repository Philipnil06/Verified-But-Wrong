def process_payment_event(state: dict, event: dict) -> dict:
    updated_state = {
        "balances": dict((state or {}).get("balances", {})),
        "processed_event_ids": list((state or {}).get("processed_event_ids", [])),
        "failed_events": list((state or {}).get("failed_events", [])),
    }
    merchant_id = event.get("merchant_id")
    amount = float(event.get("amount", 0.0))
    if event.get("status") == "succeeded":
        updated_state["balances"][merchant_id] = updated_state["balances"].get(merchant_id, 0.0) + amount
        return {"status": "ok", "message": "Payment credited.", "state": updated_state}
    if event.get("status") == "failed":
        return {"status": "ignored", "message": "Failed payment ignored.", "state": updated_state}
    return {"status": "error", "message": "Unknown status.", "state": updated_state}
