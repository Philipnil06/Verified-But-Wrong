Implement invoice cancellation behavior.

- Mark a cancellable invoice as cancelled.
- Reject invalid invoice identifiers.
- Return the updated invoice state.

Acceptance criteria:
- A normal invoice can be cancelled.
- Cancelled status is persisted.
- Invalid inputs fail.

This extracted public spec intentionally leaves downstream state-restoration requirements unstated.
