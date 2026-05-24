"""Task-specific intended oracle for DA0208."""


def _optimal_box_size(sizes, k):
    sizes = tuple(sorted(sizes))
    n = len(sizes)
    pairs_needed = n - k

    best = float("inf")

    def rec(remaining, pairs_left, current_max):
        nonlocal best
        if current_max >= best:
            return
        if not remaining:
            best = min(best, current_max)
            return
        # Leave smallest as single if we still can.
        singles_left = len(remaining) - 2 * pairs_left
        first = remaining[0]
        if singles_left > 0:
            rec(remaining[1:], pairs_left, max(current_max, first))
        if pairs_left > 0:
            for j in range(1, len(remaining)):
                pair_sum = first + remaining[j]
                nxt = remaining[1:j] + remaining[j + 1 :]
                rec(nxt, pairs_left - 1, max(current_max, pair_sum))

    rec(sizes, pairs_needed, 0)
    return int(best)


def run_tests(candidate):
    tests = [
        (3, 2, [2, 3, 5]),
        (4, 2, [1, 2, 7, 9]),
        (5, 3, [1, 1, 1, 1, 10]),
    ]
    rows = []
    for n, k, sizes in tests:
        got = candidate(n, k, sizes)
        want = _optimal_box_size(sizes, k)
        rows.append(
            {
                "input": repr((n, k, sizes)),
                "expected": want,
                "actual": got,
                "intended_oracle_pass": got == want,
                "oracle_note": "NL requires minimum uniform box capacity that can pack all cowbells.",
            }
        )
    return rows
