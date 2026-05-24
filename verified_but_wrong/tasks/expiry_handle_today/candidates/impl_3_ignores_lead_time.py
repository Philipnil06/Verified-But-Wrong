from datetime import datetime


def _parse_date(value: str):
    return datetime.strptime(value, "%Y-%m-%d").date()


def should_handle_today(item: dict, today: str) -> dict:
    if not isinstance(item, dict):
        return {"status": "error", "handle_today": None, "message": "Item is invalid."}
    try:
        today_date = _parse_date(today)
        expiry_date = _parse_date(item.get("expiry_date"))
    except (TypeError, ValueError):
        return {"status": "error", "handle_today": None, "message": "Invalid date."}

    return {
        "status": "ok",
        "handle_today": expiry_date <= today_date,
        "message": "Checked expiry date without lead time.",
    }
