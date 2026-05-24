def apply_discount(price: float, discount_percent: float) -> dict:
    if price < 0:
        return {"status": "error", "final_price": None, "message": "Price must be non negative."}

    final_price = price * (1 - discount_percent / 100)
    return {"status": "ok", "final_price": final_price, "message": "Discount applied."}
