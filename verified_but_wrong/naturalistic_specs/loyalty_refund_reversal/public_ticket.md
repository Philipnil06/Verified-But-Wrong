# Product ticket: refund processing with customer rewards

## Background
Customers may request partial or full refunds for paid orders. The refund service should update the order refund state and return a clear success or error result.

## Happy path
- Paid orders can be refunded.
- Refund amount must be positive.
- Refund amount must not exceed the remaining paid amount.
- Successful refunds update `refunded_total`.

## Policy note
Customer reward balances are maintained by a separate account service.

## Acceptance criteria
- A valid partial refund succeeds.
- Over-refunds fail.
- Cancelled orders fail.
