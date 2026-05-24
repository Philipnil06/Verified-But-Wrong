"""Weak-spec proxy scaffold.

This proxy only models the suspicious trivial/range postcondition pattern
identified by the scanner. It is not a full Dafny verification reproduction.
"""


def run_tests(candidate):
    inputs = [(), (1,), (1, 2), ([1, 2, 3],)]
    rows = []
    for args in inputs:
        try:
            actual = candidate(*args)
            ok = isinstance(actual, int) and actual >= 0
        except Exception as exc:
            actual = repr(exc)
            ok = False
        rows.append({
            "input": repr(args),
            "actual": actual,
            "weak_spec_proxy_pass": ok,
            "proxy_note": "generic non-negative-result proxy; human must replace with task-specific proxy if needed",
        })
    return rows
