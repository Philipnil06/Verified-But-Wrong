def apply_discount(price: float, discount_percent: float) -> dict:
    final_price = price * (1 - discount_percent / 100)
    return {"status": "ok", "final_price": final_price, "message": "Discount applied."}
