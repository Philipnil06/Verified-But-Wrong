def apply_discount(price: float, discount_percent: float) -> dict:
    if price < 0:
        return {"status": "error", "final_price": None, "message": "Price must be non negative."}
    if discount_percent < 0 or discount_percent > 100:
        return {"status": "error", "final_price": None, "message": "Discount percent must be between 0 and 100."}

    final_price = int(price * (1 - discount_percent / 100))
    return {"status": "ok", "final_price": float(final_price), "message": "Discount applied with integer rounding."}
