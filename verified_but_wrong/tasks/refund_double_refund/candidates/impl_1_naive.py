def refund(order: dict, amount: float) -> dict:
    if amount <= 0:
        return {
            "status": "error",
            "message": "Refund amount must be positive.",
            "order": order,
        }

    return {
        "status": "ok",
        "message": "Refund accepted.",
        "order": order,
    }
