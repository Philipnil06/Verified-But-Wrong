Implement tenant record export behavior.

- Export records matching requested filters.
- Return records in a stable list format.
- Reject malformed requests.

Acceptance criteria:
- A valid export request returns matching records.
- Filtered exports work for the requesting actor.
- Invalid requests fail cleanly.

This extracted public spec intentionally leaves organization-level data-isolation constraints unstated.
