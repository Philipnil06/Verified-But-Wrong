from pathlib import Path
import importlib.util


_SPEC_PATH = Path(__file__).resolve().parent / "public_spec_naive.py"
_SPEC = importlib.util.spec_from_file_location("loyalty_public_spec_naive_helpers", _SPEC_PATH)
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)
_customer = _MOD._customer
_order = _MOD._order
_record = _MOD._record
_summarize = _MOD._summarize


def run_tests(candidate_func) -> dict:
    tests = []
    result = candidate_func(_order(), _customer(), 250.0)
    order = result.get("order") or {}
    tests.append(_record("valid_refund_succeeds", result.get("status") == "ok", "status=ok", f"status={result.get('status')}"))

    negative = candidate_func(_order(), _customer(), -1.0)
    tests.append(_record("amount_must_be_positive", negative.get("status") == "error", "status=error", f"status={negative.get('status')}"))

    over = candidate_func(_order(refunded_total=900.0), _customer(), 200.0)
    tests.append(_record("refund_cannot_exceed_remaining_paid_amount", over.get("status") == "error", "status=error", f"status={over.get('status')}"))

    tests.append(_record("refunded_total_updates", order.get("refunded_total") == 250.0, "refunded_total=250.0", f"refunded_total={order.get('refunded_total')}"))

    cancelled = candidate_func(_order(status="cancelled"), _customer(), 100.0)
    chargeback = candidate_func(_order(status="chargeback"), _customer(), 100.0)
    tests.append(_record("cancelled_or_chargeback_orders_fail", cancelled.get("status") == "error" and chargeback.get("status") == "error", "both statuses=error", f"cancelled={cancelled.get('status')}, chargeback={chargeback.get('status')}"))
    return _summarize(tests)
