from __future__ import annotations

from external_cases._benchmark_proxy import public_run_tests


def run_tests(candidate_func):
    return public_run_tests("payment_webhook_idempotency", candidate_func)
