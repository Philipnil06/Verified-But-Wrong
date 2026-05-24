from datetime import datetime, timedelta


def _parse_date(value: str):
    return datetime.strptime(value, "%Y-%m-%d").date()


def should_handle_today(item: dict, today: str) -> dict:
    if not isinstance(item, dict):
        return {"status": "error", "handle_today": None, "message": "Item is invalid."}

    try:
        today_date = _parse_date(today)
        expiry_date = _parse_date(item.get("expiry_date"))
        lead_time = int(item.get("category_lead_time_days", 0))
    except (TypeError, ValueError):
        return {"status": "error", "handle_today": None, "message": "Invalid date or lead time."}

    if lead_time < 0:
        return {"status": "error", "handle_today": None, "message": "Lead time must be non negative."}

    handle_date = expiry_date - timedelta(days=lead_time)
    return {
        "status": "ok",
        "handle_today": handle_date <= today_date or expiry_date < today_date,
        "message": "Checked expiry date with lead time.",
    }
