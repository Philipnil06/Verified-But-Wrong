# Evaluation Freeze

- gate version: policy_gate_v1
- freeze date: 2026-05-11

## Development Tasks

- refund_double_refund
- access_control_delete_user
- discount_nonnegative_price
- rate_limiter_boundary
- expiry_handle_today
- payment_webhook_idempotency
- refund_window_expiry
- loyalty_refund_reversal

## Heldout Executable Tasks

- tenant_isolation_export
- role_downgrade_session_invalidation
- audit_log_retention_delete_user
- invoice_cancellation_stock_restore

## Naturalistic Product-Ticket-Style Docs

- access_control_delete_user
- audit_log_delete_ticket
- expiry_handle_today
- invoice_cancel_stock_ticket
- loyalty_refund_reversal
- loyalty_refund_safe_ticket
- payment_webhook_idempotency
- rate_limiter_boundary
- refund_window_expiry
- role_downgrade_ticket
- tenant_export_safe_ticket
- tenant_export_ticket

## External Docs

None currently. Existing naturalistic docs are author-created product-ticket-style fixtures unless explicitly marked otherwise in provenance.

## Gate Allowed Inputs

- public spec text
- policy pack cards
- task category / split metadata

## Gate Forbidden Inputs

- hidden oracle
- selected candidate
- verified_but_wrong outcome
- candidate source code

## Metrics Reported

- VBW rate
- dangerous catch / escape rate
- safe allow rate
- safe review/block burden
- repair success rate
- high/critical dangerous catch rate

## Freeze Rule

After thresholds and policy logic are frozen, heldout tasks/docs are evaluated once and reported. This file records the intended split and artifact-access boundary.
