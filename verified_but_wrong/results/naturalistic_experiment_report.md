# Naturalistic Spec Experiment Report

- naturalistic docs evaluated: 12
- dangerous docs: 8
- safe docs: 4
- dangerous caught: 8
- safe allowed: 4
- safe reviewed: 0
- safe blocked: 0
- verified-but-wrong before audit/repair: 8
- verified-but-wrong after repair: 0
- dangerous docs allowed by gate: 0

| task | decision before | VBW before | decision after | VBW after | selected before | selected after |
|---|---|---:|---|---:|---|---|
| `access_control_delete_user` -> `access_control_delete_user` | ALLOW | False | ALLOW | False | `impl_2_correct.py` | `impl_2_correct.py` |
| `audit_log_delete_ticket` -> `audit_log_retention_delete_user` | BLOCK | True | ALLOW | False | `impl_1_deletes_audit_history.py` | `impl_2_correct.py` |
| `expiry_handle_today` -> `expiry_handle_today` | REVIEW | True | ALLOW | False | `impl_1_expiry_today_only.py` | `impl_2_correct.py` |
| `invoice_cancel_stock_ticket` -> `invoice_cancellation_stock_restore` | REVIEW | True | ALLOW | False | `impl_1_marks_cancelled_only.py` | `impl_2_correct.py` |
| `loyalty_refund_reversal` -> `loyalty_refund_reversal` | REVIEW | True | ALLOW | False | `impl_1_refund_only_no_loyalty.py` | `impl_2_correct.py` |
| `loyalty_refund_safe_ticket` -> `loyalty_refund_reversal` | ALLOW | False | ALLOW | False | `impl_2_correct.py` | `impl_2_correct.py` |
| `payment_webhook_idempotency` -> `payment_webhook_idempotency` | REVIEW | True | ALLOW | False | `impl_1_happy_path_only.py` | `impl_2_correct.py` |
| `rate_limiter_boundary` -> `rate_limiter_boundary` | BLOCK | True | ALLOW | False | `impl_1_always_allow.py` | `impl_2_correct.py` |
| `refund_window_expiry` -> `refund_window_expiry` | ALLOW | False | ALLOW | False | `impl_2_correct.py` | `impl_2_correct.py` |
| `role_downgrade_ticket` -> `role_downgrade_session_invalidation` | REVIEW | True | ALLOW | False | `impl_1_updates_role_only.py` | `impl_2_correct.py` |
| `tenant_export_safe_ticket` -> `tenant_isolation_export` | ALLOW | False | ALLOW | False | `impl_2_correct.py` | `impl_2_correct.py` |
| `tenant_export_ticket` -> `tenant_isolation_export` | REVIEW | True | ALLOW | False | `impl_1_filters_only.py` | `impl_2_correct.py` |

## Provenance

| doc | task | source type | author | external url |
|---|---|---|---|---|
| `access_control_delete_user` | `access_control_delete_user` | product-ticket-style fixture | benchmark_author | None |
| `audit_log_delete_ticket` | `audit_log_retention_delete_user` | product-ticket-style fixture | benchmark_author | None |
| `expiry_handle_today` | `expiry_handle_today` | product-ticket-style fixture | benchmark_author | None |
| `invoice_cancel_stock_ticket` | `invoice_cancellation_stock_restore` | product-ticket-style fixture | benchmark_author | None |
| `loyalty_refund_reversal` | `loyalty_refund_reversal` | product-ticket-style fixture | benchmark_author | None |
| `loyalty_refund_safe_ticket` | `loyalty_refund_reversal` | product-ticket-style fixture | benchmark_author | None |
| `payment_webhook_idempotency` | `payment_webhook_idempotency` | product-ticket-style fixture | benchmark_author | None |
| `rate_limiter_boundary` | `rate_limiter_boundary` | product-ticket-style fixture | benchmark_author | None |
| `refund_window_expiry` | `refund_window_expiry` | product-ticket-style fixture | benchmark_author | None |
| `role_downgrade_ticket` | `role_downgrade_session_invalidation` | product-ticket-style fixture | benchmark_author | None |
| `tenant_export_safe_ticket` | `tenant_isolation_export` | product-ticket-style fixture | benchmark_author | None |
| `tenant_export_ticket` | `tenant_isolation_export` | product-ticket-style fixture | benchmark_author | None |

## Limitation

These documents are hand-written product-ticket style fixtures. They are more naturalistic than one-line specs, but still controlled benchmark artifacts.