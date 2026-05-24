"""Weak-spec proxy for DA0003: only checks non-negativity."""


def run_tests(candidate):
    inputs = [(10, 2, 3, 5, 7), (7, 2, 5, 100, 1), (1, 1, 1, 1, 1)]
    rows = []
    for args in inputs:
        try:
            actual = candidate(*args)
            ok = isinstance(actual, int) and actual >= 0
        except Exception as exc:
            actual = repr(exc)
            ok = False
        rows.append({"input": repr(args), "actual": actual, "weak_spec_proxy_pass": ok, "proxy_note": "models weak formal target: ensures result >= 0"})
    return rows
