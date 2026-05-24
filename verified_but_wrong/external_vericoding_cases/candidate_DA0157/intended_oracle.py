"""Task-specific intended oracle for DA0157."""


def _best_area(n: int, a: int, b: int) -> int:
    target = 6 * n
    lo = min(a, b)
    hi = max(target + 2, max(a, b) + 2)
    best = None
    for x in range(lo, hi + 1):
        y = max((target + x - 1) // x, min(a, b))
        area = x * y
        if area < target:
            continue
        if not ((x >= a and y >= b) or (x >= b and y >= a)):
            continue
        if best is None or area < best:
            best = area
    return best if best is not None else target


def run_tests(candidate):
    tests = [(1, 1, 1), (5, 2, 3), (10, 7, 8)]
    rows = []
    for n, a, b in tests:
        got = candidate(n, a, b)
        expected_area = _best_area(n, a, b)
        actual_area = got[0] if isinstance(got, (list, tuple)) and len(got) == 3 else None
        pass_exact = actual_area == expected_area
        rows.append(
            {
                "input": repr((n, a, b)),
                "expected_min_area": expected_area,
                "actual": got,
                "intended_oracle_pass": pass_exact,
                "oracle_note": "NL requires minimum possible area, not merely a valid enlarged room.",
            }
        )
    return rows
