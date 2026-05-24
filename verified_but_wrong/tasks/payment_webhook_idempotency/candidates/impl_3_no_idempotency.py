def process_payment_event(state: dict, event: dict) -> dict:
    updated_state = {
        "balances": dict((state or {}).get("balances", {})),
        "processed_event_ids": list((state or {}).get("processed_event_ids", [])),
        "failed_events": list((state or {}).get("failed_events", [])),
    }
    if not event.get("event_id"):
        return {"status": "error", "message": "Missing event_id.", "state": updated_state}
    if float(event.get("amount", 0.0)) <= 0:
        return {"status": "error", "message": "Amount must be positive.", "state": updated_state}
    if event.get("currency") != "SEK":
        return {"status": "error", "message": "Unsupported currency.", "state": updated_state}
    if event.get("status") == "failed":
        updated_state["failed_events"].append(event["event_id"])
        return {"status": "ignored", "message": "Failed payment ignored.", "state": updated_state}
    if event.get("status") != "succeeded":
        return {"status": "error", "message": "Unknown status.", "state": updated_state}

    merchant_id = event.get("merchant_id")
    updated_state["balances"][merchant_id] = updated_state["balances"].get(merchant_id, 0.0) + float(event["amount"])
    return {"status": "ok", "message": "Payment credited.", "state": updated_state}
