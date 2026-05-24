def process_payment_event(state: dict, event: dict) -> dict:
    updated_state = {
        "balances": dict((state or {}).get("balances", {})),
        "processed_event_ids": list((state or {}).get("processed_event_ids", [])),
        "failed_events": list((state or {}).get("failed_events", [])),
    }
    event_id = event.get("event_id")
    if not event_id:
        return {"status": "error", "message": "Missing event_id.", "state": updated_state}
    if event_id in updated_state["processed_event_ids"]:
        return {"status": "ignored", "message": "Event already processed.", "state": updated_state}
    if float(event.get("amount", 0.0)) <= 0:
        return {"status": "error", "message": "Amount must be positive.", "state": updated_state}
    if event.get("currency") != "SEK":
        return {"status": "error", "message": "Unsupported currency.", "state": updated_state}

    merchant_id = event.get("merchant_id")
    updated_state["balances"][merchant_id] = updated_state["balances"].get(merchant_id, 0.0) + float(event["amount"])
    updated_state["processed_event_ids"].append(event_id)
    return {"status": "ok", "message": "Payment credited.", "state": updated_state}
