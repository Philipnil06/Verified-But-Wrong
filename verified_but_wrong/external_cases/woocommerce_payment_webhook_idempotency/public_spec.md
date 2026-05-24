Implement payment event processing behavior.

- Successful payment events should increase merchant balance by the event amount.
- Failed payment events should not increase merchant balance.
- Invalid requests should fail safely.

Acceptance criteria:
- Successful payment events update the balance.
- Failed payment events do not update the balance.
- Invalid requests fail cleanly.

This extracted public spec intentionally leaves duplicate-handling rules unstated.
