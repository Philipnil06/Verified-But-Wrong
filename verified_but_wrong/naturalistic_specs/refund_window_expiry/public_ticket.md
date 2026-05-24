# Product ticket: refund eligibility window

## Background
Finance allows normal refunds for paid orders. The service should calculate eligibility and update the refunded total.

## Happy path
- Paid orders can be refunded.
- Refund amount must be positive.
- Refund amount cannot exceed remaining paid amount.
- Successful refunds update `refunded_total`.

## Policy note
Refund policy is based on purchase date. Manual override may apply for exceptional support cases.

## Acceptance criteria
- Valid refund succeeds.
- Over-refund fails.
- Cancelled and chargeback orders fail.
