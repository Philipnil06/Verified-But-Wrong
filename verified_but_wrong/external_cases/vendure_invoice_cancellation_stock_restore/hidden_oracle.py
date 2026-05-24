from __future__ import annotations

from external_cases._benchmark_proxy import hidden_run_tests


def run_tests(candidate_func):
    return hidden_run_tests("invoice_cancellation_stock_restore", candidate_func)
