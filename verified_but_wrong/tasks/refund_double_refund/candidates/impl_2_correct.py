def refund(order: dict, amount: float) -> dict:
    if amount <= 0:
        return {
            "status": "error",
            "message": "Refund amount must be positive.",
            "order": order,
        }

    if not isinstance(order, dict):
        return {
            "status": "error",
            "message": "Order is invalid.",
            "order": order,
        }

    if order.get("status") != "paid":
        return {
            "status": "error",
            "message": "Only paid orders can be refunded.",
            "order": order,
        }

    original_payment = float(order.get("original_payment", 0.0))
    refunded_total = float(order.get("refunded_total", 0.0))

    if refunded_total >= original_payment:
        return {
            "status": "error",
            "message": "Order has already been fully refunded.",
            "order": order,
        }

    if refunded_total + amount > original_payment:
        return {
            "status": "error",
            "message": "Refund exceeds remaining refundable balance.",
            "order": order,
        }

    updated_order = dict(order)
    updated_total = refunded_total + amount
    updated_order["refunded_total"] = updated_total
    if updated_total == original_payment:
        updated_order["status"] = "refunded"

    return {
        "status": "ok",
        "message": "Refund accepted.",
        "order": updated_order,
    }
