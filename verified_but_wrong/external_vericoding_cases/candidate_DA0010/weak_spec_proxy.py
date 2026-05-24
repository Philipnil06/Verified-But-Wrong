"""Weak-spec proxy for DA0010: range + edge cases only."""


def run_tests(candidate):
    tests = [(1, 0), (1, 3), (3, 1), (4, 8)]
    rows = []
    for n, t in tests:
        try:
            got = candidate(n, t)
            total = n * (n + 1) // 2
            ok = isinstance(got, int) and 0 <= got <= total
            ok = ok and (t != 0 or got == 0)
            ok = ok and (n != 1 or (got == 0 if t == 0 else got == 1))
            ok = ok and (not (t >= 1 and n > 1) or got >= 1)
        except Exception as exc:
            got = repr(exc)
            ok = False
        rows.append({"input": repr((n, t)), "actual": got, "weak_spec_proxy_pass": ok, "proxy_note": "models ValidResult + CorrectForEdgeCases only"})
    return rows
