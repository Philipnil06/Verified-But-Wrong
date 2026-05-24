def process_refund(order: dict, customer: dict, amount: float) -> dict:
    return {"status": "error", "message": "Refund rejected.", "order": order, "customer": customer}
