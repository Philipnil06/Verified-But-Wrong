# Ticket: refund with rewards

Refunds must update refunded_total and cannot exceed the remaining paid amount. If the purchase awarded loyalty points, the refunded portion must reverse proportional loyalty points without making the customer balance negative.

Acceptance criteria:
- Partial refund reverses proportional points.
- Over-refund fails.
- Cancelled orders fail.
