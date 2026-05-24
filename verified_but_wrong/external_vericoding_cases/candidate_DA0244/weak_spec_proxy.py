"""Adapted spec check for DA0244: only non-negativity."""


def run_tests(candidate):
    tests = [(3, [0, 1, 0]), (4, [0, 0, 1, 0]), (3, [0, 0, 0])]
    rows = []
    for n, m in tests:
        try:
            got = candidate(n, m)
            ok = isinstance(got, int) and got >= 0
        except Exception as exc:
            got = repr(exc)
            ok = False
        rows.append(
            {
                "input": repr((n, m)),
                "actual": got,
                "weak_spec_proxy_pass": ok,
                "proxy_note": "models weak formal target: ensures result >= 0",
            }
        )
    return rows
