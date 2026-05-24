"""Adapted spec check for DA0293: only output range."""


def run_tests(candidate):
    tests = [(5, 1, "00101"), (6, 2, "010101"), (4, 0, "1111")]
    rows = []
    for n, k, s in tests:
        try:
            got = candidate(n, k, s)
            ok = isinstance(got, int) and 0 <= got <= n
        except Exception as exc:
            got = repr(exc)
            ok = False
        rows.append(
            {
                "input": repr((n, k, s)),
                "actual": got,
                "weak_spec_proxy_pass": ok,
                "proxy_note": "models weak formal target: 0 <= result <= N",
            }
        )
    return rows
