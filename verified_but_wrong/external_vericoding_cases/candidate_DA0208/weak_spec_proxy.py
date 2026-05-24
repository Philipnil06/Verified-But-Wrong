"""Weak-spec proxy for DA0208: only checks non-negativity."""


def run_tests(candidate):
    tests = [(3, 2, [2, 3, 5]), (4, 2, [1, 2, 7, 9]), (5, 3, [1, 1, 1, 1, 10])]
    rows = []
    for n, k, sizes in tests:
        try:
            got = candidate(n, k, sizes)
            ok = isinstance(got, int) and got >= 0
        except Exception as exc:
            got = repr(exc)
            ok = False
        rows.append({"input": repr((n, k, sizes)), "actual": got, "weak_spec_proxy_pass": ok, "proxy_note": "models weak formal target: ensures result >= 0"})
    return rows
