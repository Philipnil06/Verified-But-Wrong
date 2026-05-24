from datetime import datetime


def _parse_date(value: str):
    return datetime.strptime(value, "%Y-%m-%d").date()


def process_refund(order: dict, amount: float, current_date: str) -> dict:
    if amount <= 0:
        return {"status": "error", "message": "Amount must be positive.", "order": order}
    if not isinstance(order, dict) or order.get("status") != "paid":
        return {"status": "error", "message": "Only paid orders can be refunded.", "order": order}

    try:
        days_since_purchase = (_parse_date(current_date) - _parse_date(order.get("purchase_date"))).days
    except (TypeError, ValueError):
        return {"status": "error", "message": "Invalid date.", "order": order}

    if days_since_purchase > 30:
        return {"status": "error", "message": "Refund window expired.", "order": order}

    remaining = float(order.get("original_payment", 0.0)) - float(order.get("refunded_total", 0.0))
    if amount > remaining:
        return {"status": "error", "message": "Refund exceeds remaining paid amount.", "order": order}

    updated = dict(order)
    updated["refunded_total"] = float(updated.get("refunded_total", 0.0)) + amount
    return {"status": "ok", "message": "Refund processed.", "order": updated}
