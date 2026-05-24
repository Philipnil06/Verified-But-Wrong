"""Adapted spec check for DA0306: only length equality."""


def run_tests(candidate):
    tests = ["bacde", "ehllo", "lrc"]
    rows = []
    for t in tests:
        try:
            got = candidate(t)
            ok = isinstance(got, str) and len(got) == len(t)
        except Exception as exc:
            got = repr(exc)
            ok = False
        rows.append(
            {
                "input": repr((t,)),
                "actual": got,
                "weak_spec_proxy_pass": ok,
                "proxy_note": "models weak formal target: |result| == |t|",
            }
        )
    return rows
