"""Task-specific intended oracle for DA0244."""


def _expected_min_sum_below(m):
    # Uses the preamble model: choose nondecreasing dm with dm[i] >= m[i] + 1
    # to minimize SumBelow = sum(dm[i] - 1 - m[i]).
    dm = []
    for i, x in enumerate(m):
        need = x + 1
        dm.append(need if i == 0 else max(dm[-1], need))
    return sum(dm[i] - 1 - m[i] for i in range(len(m)))


def run_tests(candidate):
    tests = [(3, [0, 1, 0]), (4, [0, 0, 1, 0]), (3, [0, 0, 0])]
    rows = []
    for n, m in tests:
        got = candidate(n, m)
        want = _expected_min_sum_below(m)
        rows.append(
            {
                "input": repr((n, m)),
                "expected": want,
                "actual": got,
                "intended_oracle_pass": got == want,
                "oracle_note": "NL requires minimizing the total below-water marks across days.",
            }
        )
    return rows
