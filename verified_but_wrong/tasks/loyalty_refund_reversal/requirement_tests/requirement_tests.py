from pathlib import Path
import importlib.util


_SPEC_PATH = Path(__file__).resolve().parents[1] / "specs" / "public_spec_naive.py"
_SPEC = importlib.util.spec_from_file_location("loyalty_requirement_helpers", _SPEC_PATH)
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)
_order = _MOD._order
_customer = _MOD._customer
_record = _MOD._record


def valid_refund_succeeds(candidate_func) -> dict:
    result = candidate_func(_order(), _customer(), 250.0)
    return _record("valid_refund_succeeds", result.get("status") == "ok", "status=ok", f"status={result.get('status')}")


def refund_cannot_exceed_remaining(candidate_func) -> dict:
    result = candidate_func(_order(refunded_total=900.0), _customer(), 200.0)
    return _record("refund_cannot_exceed_remaining_paid_amount", result.get("status") == "error", "status=error", f"status={result.get('status')}")


def refunded_total_updates(candidate_func) -> dict:
    result = candidate_func(_order(), _customer(), 250.0)
    order = result.get("order") or {}
    return _record("successful_refunds_update_refunded_total", order.get("refunded_total") == 250.0, "refunded_total=250.0", f"refunded_total={order.get('refunded_total')}")


def proportional_loyalty_reversal(candidate_func) -> dict:
    result = candidate_func(_order(), _customer(), 250.0)
    customer = result.get("customer") or {}
    return _record("successful_refunds_reverse_proportional_loyalty_points", customer.get("loyalty_points") == 75, "loyalty_points=75", f"loyalty_points={customer.get('loyalty_points')}")


def loyalty_points_non_negative(candidate_func) -> dict:
    result = candidate_func(_order(), _customer(points=10), 250.0)
    customer = result.get("customer") or {}
    return _record("loyalty_points_must_not_become_negative", customer.get("loyalty_points", -1) >= 0, "loyalty_points>=0", f"loyalty_points={customer.get('loyalty_points')}")


def cancelled_or_chargeback_fail(candidate_func) -> dict:
    cancelled = candidate_func(_order(status="cancelled"), _customer(), 100.0)
    chargeback = candidate_func(_order(status="chargeback"), _customer(), 100.0)
    passed = cancelled.get("status") == "error" and chargeback.get("status") == "error"
    return _record("cancelled_or_chargeback_orders_cannot_be_refunded", passed, "both statuses=error", f"cancelled={cancelled.get('status')}, chargeback={chargeback.get('status')}")


REQUIREMENT_TESTS = {
    "Valid refund succeeds": valid_refund_succeeds,
    "Refund cannot exceed remaining paid amount": refund_cannot_exceed_remaining,
    "Successful refunds must update refunded_total": refunded_total_updates,
    "Successful refunds must reverse proportional loyalty points awarded by the original purchase": proportional_loyalty_reversal,
    "Loyalty points must not become negative": loyalty_points_non_negative,
    "Cancelled or chargeback orders cannot be refunded": cancelled_or_chargeback_fail,
}
