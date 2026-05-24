"""Task-specific intended oracle for DA0293."""


def _flip_segment(s: str, l: int, r: int) -> str:
    out = list(s)
    for i in range(l, r + 1):
        out[i] = "1" if out[i] == "0" else "0"
    return "".join(out)


def _max_run_ones(s: str) -> int:
    best = cur = 0
    for ch in s:
        if ch == "1":
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return best


def _expected(n: int, k: int, s: str) -> int:
    states = {s}
    for _ in range(k):
        nxt = set(states)
        for st in states:
            for i in range(n):
                for j in range(i, n):
                    nxt.add(_flip_segment(st, i, j))
        states = nxt
    return max(_max_run_ones(st) for st in states)


def run_tests(candidate):
    tests = [(5, 1, "00101"), (6, 2, "010101"), (4, 0, "1111")]
    rows = []
    for n, k, s in tests:
        got = candidate(n, k, s)
        want = _expected(n, k, s)
        rows.append(
            {
                "input": repr((n, k, s)),
                "expected": want,
                "actual": got,
                "intended_oracle_pass": got == want,
                "oracle_note": "NL requires maximizing consecutive ones after at most K range flips.",
            }
        )
    return rows
