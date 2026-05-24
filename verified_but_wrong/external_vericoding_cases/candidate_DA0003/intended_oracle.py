"""Task-specific intended oracle for DA0003."""


def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a


def _lcm(a: int, b: int) -> int:
    return a // _gcd(a, b) * b


def expected(n: int, a: int, b: int, p: int, q: int) -> int:
    common = n // _lcm(a, b)
    only_a = n // a - common
    only_b = n // b - common
    return only_a * p + only_b * q + common * max(p, q)


def run_tests(candidate):
    tests = [
        (5, 2, 3, 4, 5),
        (10, 2, 5, 3, 8),
        (12, 3, 4, 7, 2),
    ]
    rows = []
    for args in tests:
        got = candidate(*args)
        want = expected(*args)
        rows.append(
            {
                "input": repr(args),
                "expected": want,
                "actual": got,
                "intended_oracle_pass": got == want,
                "oracle_note": "NL requires maximizing total chocolates under divisibility/tie rule.",
            }
        )
    return rows
