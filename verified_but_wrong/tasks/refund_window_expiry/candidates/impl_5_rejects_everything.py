def process_refund(order: dict, amount: float, current_date: str) -> dict:
    return {"status": "error", "message": "Refund rejected.", "order": order}
