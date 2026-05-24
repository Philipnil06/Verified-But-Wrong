"""Weak-spec proxy for DA0157: checks ValidOutput-style constraints only."""


def run_tests(candidate):
    tests = [(1, 1, 1), (5, 2, 3), (10, 7, 8)]
    rows = []
    for n, a, b in tests:
        try:
            got = candidate(n, a, b)
            ok = isinstance(got, (list, tuple)) and len(got) == 3
            if ok:
                area, x, y = got
                ok = (isinstance(area, int) and isinstance(x, int) and isinstance(y, int) and area >= 6 * n and x > 0 and y > 0 and area == x * y and ((x >= a and y >= b) or (x >= b and y >= a)))
        except Exception as exc:
            got = repr(exc)
            ok = False
        rows.append({"input": repr((n, a, b)), "actual": got, "weak_spec_proxy_pass": ok, "proxy_note": "models shape/range/output-structure but not minimality"})
    return rows
