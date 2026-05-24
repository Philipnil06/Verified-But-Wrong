"""Candidate-only bad implementation scaffold for DA0082.

This is intentionally wrong under the NL intent. It is not validation by itself.
A human must inspect the external task and write a task-specific intended_oracle.py
before this case can be marked validated.
"""


def candidate(*args, **kwargs):
    """Return a constant value likely to satisfy very weak non-negativity specs."""
    return 0
