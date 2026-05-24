from pathlib import Path
import importlib.util


_SPEC_PATH = Path(__file__).resolve().parent / "public_spec_naive.py"
_SPEC = importlib.util.spec_from_file_location("loyalty_public_spec_naive_helpers_hidden", _SPEC_PATH)
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)
_customer = _MOD._customer
_order = _MOD._order
_record = _MOD._record
_summarize = _MOD._summarize


def run_tests(candidate_func) -> dict:
    tests = []
    partial = candidate_func(_order(), _customer(), 250.0)
    partial_customer = partial.get("customer") or {}
    tests.append(_record("valid_partial_refund_reverses_proportional_loyalty", partial.get("status") == "ok" and partial_customer.get("loyalty_points") == 75, "status=ok, loyalty_points=75", f"status={partial.get('status')}, loyalty_points={partial_customer.get('loyalty_points')}"))

    full = candidate_func(_order(), _customer(), 1000.0)
    full_customer = full.get("customer") or {}
    tests.append(_record("full_refund_reverses_all_loyalty", full.get("status") == "ok" and full_customer.get("loyalty_points") == 0, "status=ok, loyalty_points=0", f"status={full.get('status')}, loyalty_points={full_customer.get('loyalty_points')}"))

    non_negative = candidate_func(_order(), _customer(points=10), 250.0)
    non_negative_customer = non_negative.get("customer") or {}
    tests.append(_record("loyalty_points_never_negative", non_negative_customer.get("loyalty_points", -1) >= 0, "loyalty_points>=0", f"loyalty_points={non_negative_customer.get('loyalty_points')}"))

    update = candidate_func(_order(), _customer(), 250.0)
    update_order = update.get("order") or {}
    tests.append(_record("refund_updates_refunded_total", update_order.get("refunded_total") == 250.0, "refunded_total=250.0", f"refunded_total={update_order.get('refunded_total')}"))

    over = candidate_func(_order(refunded_total=900.0), _customer(), 200.0)
    tests.append(_record("refund_exceeding_remaining_fails", over.get("status") == "error", "status=error", f"status={over.get('status')}"))

    cancelled = candidate_func(_order(status="cancelled"), _customer(), 100.0)
    tests.append(_record("cancelled_order_fails", cancelled.get("status") == "error", "status=error", f"status={cancelled.get('status')}"))

    chargeback = candidate_func(_order(status="chargeback"), _customer(), 100.0)
    tests.append(_record("chargeback_order_fails", chargeback.get("status") == "error", "status=error", f"status={chargeback.get('status')}"))

    negative = candidate_func(_order(), _customer(), -1.0)
    tests.append(_record("negative_amount_fails", negative.get("status") == "error", "status=error", f"status={negative.get('status')}"))
    return _summarize(tests)
