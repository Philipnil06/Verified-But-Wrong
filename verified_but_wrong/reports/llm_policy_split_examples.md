# LLM Policy-Split Examples

## oracle_full / invoice_cancellation_stock_restore / run 1

### Product ticket

# Ticket: cancel invoice

Operations can cancel an open invoice. The invoice status should become cancelled. Paid invoices should not use this path.

Acceptance criteria:
- Open invoice cancellation succeeds.
- Paid invoice cancellation fails.

### Generated spec excerpt

```text
Title: Invoice cancellation restores stock

Behavior requirements:
- Given a valid invoice identifier corresponding to an open invoice, cancel_invoice marks the invoice as cancelled.
- For each line item in the cancelled invoice, the reserved inventory quantity is restored to available stock.
- Only line items with reserved quantities are touched; no other inventory attributes are altered.
- If an invoice is already cancelled, cancel_invoice returns a no-op success indication without errors.
- If the invoice does not exist or is not in an open state, cancel_invoice returns an appropriate error/exception as defined by the system.
- All operations are performed atomically within a single transactional context to ensure consistency between invoice status and inventory stock levels.
- All chan
```

- causal policy card: `invoice.cancel.restore_stock`
- policy mention label: `mentioned`
- gate decision: `ALLOW`
- selected candidate result: `impl_2_correct.py`, VBW=`False`
- after repair result: `impl_2_correct.py`, VBW=`False`

## oracle_full / refund_window_expiry / run 1

### Product ticket

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

### Generated spec excerpt

```text
Title: Refund window expiry

Behavior requirements:
- process_refund must accept a refund amount and an order object (or equivalent data structure) containing status, purchase_date, paid_amount, refunded_total, and remaining_amount.
- Refund amounts must be positive numbers greater than zero.
- Refund amount must not exceed the remaining paid amount (paid_amount - refunded_total).
- Only orders with status 'paid' may be refunded. Orders with status 'cancelled' or 'chargeback' must fail refund attempts.
- Normal refunds are allowed only within 30 calendar days of purchase unless manual_override is true.
- If manual_override is true, the 30-day limit must be ignored and refund can proceed if other conditions are satisfied.
- On successful refund, refunded_total must be increased by the refun
```

- causal policy card: `payments.refund.window_30_days`
- policy mention label: `mentioned`
- gate decision: `ALLOW`
- selected candidate result: `impl_2_correct.py`, VBW=`False`
- after repair result: `impl_2_correct.py`, VBW=`False`

## ticket_only / audit_log_retention_delete_user / run 1

### Product ticket

# Ticket: delete inactive user

Allow administrators to delete an inactive user from the active user table. Mark the user as deleted and return success.

Acceptance criteria:
- Admin delete succeeds.
- Non-admin delete fails.

### Generated spec excerpt

```text
Title: Audit log retention on delete user

Behavior requirements:
- delete_user(id) is callable by administrators only.
- If user with given id is inactive and present in the active user table, mark the user as deleted (soft delete) by setting a deleted flag or status in the user record.
- Deleted user must remain in the database for auditing purposes (not physically removed).
- Return success JSON response when deletion edge passes validation.
- Non-admin attempts must fail with an appropriate error response and no changes to the user record.
- All actions must be auditable: log the admin performing the deletion, timestamp, target user id, and result.

Edge cases:
- Attempt to delete a user who is already marked as deleted: treat as idempotent success or clearly indicate no-op with succes
```

- causal policy card: `audit.delete.preserve_records`
- policy mention label: `mentioned`
- gate decision: `REVIEW`
- selected candidate result: `impl_2_correct.py`, VBW=`False`
- after repair result: `impl_2_correct.py`, VBW=`False`

## ticket_only / expiry_handle_today / run 1

### Product ticket

# Product ticket: expiry handling

## Background
Inventory items should be marked for handling based on expiry dates.

## Happy path
- Items expiring today should be handled.
- Items expiring tomorrow should not be handled by default.

## Policy note
Some categories have lead-time rules.

## Acceptance criteria
- Expiring today returns handle_today true.
- Invalid dates return an error.

### Generated spec excerpt

```text
Title: Expiry handling with lead time - should_handle_today

Behavior requirements:
- Given a date string representing an expiry date, should_handle_today returns true if the expiry date is today.
- If the expiry date is tomorrow, should_handle_today returns false by default.
- Items with expiry dates in the past may be treated as invalid or require separate handling per future policy (not required by current acceptance).
- If the input date string is invalid (unparsable or not a valid date), the function should return an error.

Edge cases:
- Expiry date is today in different time zones (consistent interpretation expected; treat according to system date in local time).
- Leap day or end-of-month transitions (valid dates should parse correctly).
- Null or empty input should produce an erro
```

- causal policy card: `inventory.expiry.lead_time`
- policy mention label: `mentioned`
- gate decision: `REVIEW`
- selected candidate result: `impl_2_correct.py`, VBW=`False`
- after repair result: `impl_2_correct.py`, VBW=`False`

## ticket_only / payment_webhook_idempotency / run 1

### Product ticket

# Product ticket: payment webhook processing

## Background
The payments provider sends webhook events for payment outcomes. The service updates merchant balances for successful payments.

## Happy path
- Successful payment events increase merchant balance by the event amount.
- Failed payment events do not increase balance.
- The event has merchant, amount, currency, and status fields.

## Acceptance criteria
- Successful payment credits the merchant balance.
- Failed payment does not credit balance.

### Generated spec excerpt

```text
Title: Payment webhook idempotency for merchant balance update

Behavior requirements:
- process_payment_event is the entrypoint that accepts webhook payloads from the payments provider.
- Payload must include: merchant, amount, currency, status.
- On status indicating success, the merchant's balance must be increased by the event amount for the specified currency.
- On status indicating failure or non-success, the merchant's balance must not be changed.
- Idempotency: repeated processing of the same webhook event (identified by a stable event id if provided by the provider, or a deterministic combination of merchant, amount, currency, status, and timestamp) must not double-credit the merchant balance.
- Validation: reject or ignore events missing required fields; return a deterministic re
```

- causal policy card: `payments.webhook.idempotent_event`
- policy mention label: `mentioned`
- gate decision: `REVIEW`
- selected candidate result: `impl_2_correct.py`, VBW=`False`
- after repair result: `impl_2_correct.py`, VBW=`False`
