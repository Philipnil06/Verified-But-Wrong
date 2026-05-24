def should_handle_today(item: dict, today: str) -> dict:
    if not isinstance(item, dict):
        return {"status": "error", "handle_today": None, "message": "Item is invalid."}
    return {
        "status": "ok",
        "handle_today": item.get("expiry_date") == today,
        "message": "Checked expiry date equality.",
    }
