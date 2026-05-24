def process_refund(order: dict, customer: dict, amount: float) -> dict:
    if amount <= 0:
        return {"status": "error", "message": "Amount must be positive.", "order": order, "customer": customer}
    if not isinstance(order, dict) or order.get("status") != "paid":
        return {"status": "error", "message": "Only paid orders can be refunded.", "order": order, "customer": customer}
    remaining = float(order.get("original_payment", 0.0)) - float(order.get("refunded_total", 0.0))
    if amount > remaining:
        return {"status": "error", "message": "Refund exceeds remaining paid amount.", "order": order, "customer": customer}
    updated_order = dict(order)
    updated_order["refunded_total"] = float(updated_order.get("refunded_total", 0.0)) + amount
    return {"status": "ok", "message": "Refund processed.", "order": updated_order, "customer": dict(customer)}
