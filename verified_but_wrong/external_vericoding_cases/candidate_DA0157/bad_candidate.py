"""Deliberately weak candidate for DA0157."""


def candidate(n: int, a: int, b: int):
    d1 = max(a, b) + 1
    d2 = max(6 * n, a, b) + 1
    return [d1 * d2, d1, d2]
