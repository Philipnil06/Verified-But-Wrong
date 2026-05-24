def _copy_state(state: dict) -> dict:
    return {
        "balances": dict((state or {}).get("balances", {})),
        "processed_event_ids": list((state or {}).get("processed_event_ids", [])),
        "failed_events": list((state or {}).get("failed_events", [])),
    }


def process_payment_event(state: dict, event: dict) -> dict:
    updated_state = _copy_state(state)
    if not isinstance(state, dict) or not isinstance(event, dict):
        return {"status": "error", "message": "Invalid state or event.", "state": updated_state}
    if not all(key in state for key in ["balances", "processed_event_ids", "failed_events"]):
        return {"status": "error", "message": "State is missing required fields.", "state": updated_state}

    event_id = event.get("event_id")
    merchant_id = event.get("merchant_id")
    amount = event.get("amount")
    currency = event.get("currency")
    status = event.get("status")

    if not event_id:
        return {"status": "error", "message": "Missing event_id.", "state": updated_state}
    if not merchant_id or amount is None or currency is None or status is None:
        return {"status": "error", "message": "Event is missing required fields.", "state": updated_state}
    if float(amount) <= 0:
        return {"status": "error", "message": "Amount must be positive.", "state": updated_state}
    if currency != "SEK":
        return {"status": "error", "message": "Unsupported currency.", "state": updated_state}
    if event_id in updated_state["processed_event_ids"]:
        return {"status": "ignored", "message": "Event already processed.", "state": updated_state}
    if status == "failed":
        if event_id not in updated_state["failed_events"]:
            updated_state["failed_events"].append(event_id)
        return {"status": "ignored", "message": "Failed payment ignored.", "state": updated_state}
    if status != "succeeded":
        return {"status": "error", "message": "Unknown payment status.", "state": updated_state}

    updated_state["balances"][merchant_id] = updated_state["balances"].get(merchant_id, 0.0) + float(amount)
    updated_state["processed_event_ids"].append(event_id)
    return {"status": "ok", "message": "Payment credited.", "state": updated_state}
