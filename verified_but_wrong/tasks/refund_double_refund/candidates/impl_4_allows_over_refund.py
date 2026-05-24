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

    updated_order = dict(order)
    updated_order["refunded_total"] = float(updated_order.get("refunded_total", 0.0)) + amount

    return {
        "status": "ok",
        "message": "Refund accepted.",
        "order": updated_order,
    }
