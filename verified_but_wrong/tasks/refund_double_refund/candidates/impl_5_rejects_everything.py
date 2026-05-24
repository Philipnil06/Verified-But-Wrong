def refund(order: dict, amount: float) -> dict:
    return {
        "status": "error",
        "message": "Refund rejected.",
        "order": order,
    }
