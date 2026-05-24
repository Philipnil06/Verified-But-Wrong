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

    original_payment = float(order.get("original_payment", 0.0))
    if amount > original_payment:
        return {
            "status": "error",
            "message": "Refund exceeds original payment.",
            "order": order,
        }

    return {
        "status": "ok",
        "message": "Refund accepted.",
        "order": order,
    }
