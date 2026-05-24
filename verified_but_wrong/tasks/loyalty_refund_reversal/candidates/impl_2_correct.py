def process_refund(order: dict, customer: dict, amount: float) -> dict:
    if amount <= 0:
        return {"status": "error", "message": "Amount must be positive.", "order": order, "customer": customer}
    if not isinstance(order, dict) or not isinstance(customer, dict):
        return {"status": "error", "message": "Invalid input.", "order": order, "customer": customer}
    if order.get("status") != "paid":
        return {"status": "error", "message": "Only paid orders can be refunded.", "order": order, "customer": customer}
    original_payment = float(order.get("original_payment", 0.0))
    refunded_total = float(order.get("refunded_total", 0.0))
    remaining = original_payment - refunded_total
    if amount > remaining:
        return {"status": "error", "message": "Refund exceeds remaining paid amount.", "order": order, "customer": customer}

    updated_order = dict(order)
    updated_customer = dict(customer)
    updated_order["refunded_total"] = refunded_total + amount
    awarded = float(order.get("loyalty_points_awarded", 0.0))
    reversed_points = round(awarded * (amount / original_payment)) if original_payment else 0
    updated_customer["loyalty_points"] = max(0, int(updated_customer.get("loyalty_points", 0)) - int(reversed_points))
    return {"status": "ok", "message": "Refund processed.", "order": updated_order, "customer": updated_customer}
