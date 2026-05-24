"""Task-specific intended oracle for DA0010."""


def _simulate_full_glasses(n: int, t: int) -> int:
    levels = [[0.0 for _ in range(i + 1)] for i in range(n)]
    for _ in range(t):
        levels[0][0] += 1.0
        for i in range(n - 1):
            for j in range(i + 1):
                if levels[i][j] > 1.0:
                    extra = levels[i][j] - 1.0
                    levels[i][j] = 1.0
                    levels[i + 1][j] += extra / 2.0
                    levels[i + 1][j + 1] += extra / 2.0
        for j in range(n):
            if levels[n - 1][j] > 1.0:
                levels[n - 1][j] = 1.0
    return sum(1 for i in range(n) for j in range(i + 1) if levels[i][j] >= 1.0 - 1e-9)


def run_tests(candidate):
    tests = [(2, 2), (3, 4), (4, 6)]
    rows = []
    for n, t in tests:
        got = candidate(n, t)
        want = _simulate_full_glasses(n, t)
        rows.append(
            {
                "input": repr((n, t)),
                "expected": want,
                "actual": got,
                "intended_oracle_pass": got == want,
                "oracle_note": "NL requires process simulation and full-glass count.",
            }
        )
    return rows
