# Candidate-Set Underconstraint Analysis

This analysis evaluates all candidate implementations for each task/spec-mode pair. Hidden oracles are used only for evaluation analysis, not for pre-selection gating.

## Aggregate Candidate-Set Underconstraint

| Spec mode | Public-passing candidates | Hidden-failing among public-passing | Mean underconstraint risk | Tasks with existence risk | Selected VBW |
|---|---:|---:|---:|---:|---:|
| `naive` | 46 | 34 | 0.74 | 12/12 | 12/12 |
| `critic` | 24 | 12 | 0.29 | 5/12 | 5/12 |
| `oracle` | 12 | 0 | 0.00 | 0/12 | 0/12 |
| `repaired_naive` | 18 | 6 | 0.25 | 6/12 | 0/12 |
| `repaired_critic` | 18 | 6 | 0.25 | 6/12 | 0/12 |

## Per-Task Candidate-Set Underconstraint

| Task | Split | Spec mode | Selected candidate | Public-passing | Hidden-failing among public-passing | Underconstraint risk | Existence risk | Selected VBW |
|---|---|---|---|---:|---:|---:|---|---|
| `access_control_delete_user` | development | `naive` | `impl_1_no_auth.py` | 4 | 3 | 0.75 | True | True |
| `access_control_delete_user` | development | `critic` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `access_control_delete_user` | development | `oracle` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `access_control_delete_user` | development | `repaired_naive` | `impl_2_correct.py` | 2 | 1 | 0.50 | True | False |
| `access_control_delete_user` | development | `repaired_critic` | `impl_2_correct.py` | 2 | 1 | 0.50 | True | False |
| `audit_log_retention_delete_user` | heldout | `naive` | `impl_1_deletes_audit_history.py` | 4 | 3 | 0.75 | True | True |
| `audit_log_retention_delete_user` | heldout | `critic` | `impl_1_deletes_audit_history.py` | 3 | 2 | 0.67 | True | True |
| `audit_log_retention_delete_user` | heldout | `oracle` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `audit_log_retention_delete_user` | heldout | `repaired_naive` | `impl_2_correct.py` | 2 | 1 | 0.50 | True | False |
| `audit_log_retention_delete_user` | heldout | `repaired_critic` | `impl_2_correct.py` | 2 | 1 | 0.50 | True | False |
| `discount_nonnegative_price` | development | `naive` | `impl_1_simple_discount.py` | 4 | 3 | 0.75 | True | True |
| `discount_nonnegative_price` | development | `critic` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `discount_nonnegative_price` | development | `oracle` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `discount_nonnegative_price` | development | `repaired_naive` | `impl_2_correct.py` | 2 | 1 | 0.50 | True | False |
| `discount_nonnegative_price` | development | `repaired_critic` | `impl_2_correct.py` | 2 | 1 | 0.50 | True | False |
| `expiry_handle_today` | development | `naive` | `impl_1_expiry_today_only.py` | 3 | 2 | 0.67 | True | True |
| `expiry_handle_today` | development | `critic` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `expiry_handle_today` | development | `oracle` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `expiry_handle_today` | development | `repaired_naive` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `expiry_handle_today` | development | `repaired_critic` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `invoice_cancellation_stock_restore` | heldout | `naive` | `impl_1_marks_cancelled_only.py` | 4 | 3 | 0.75 | True | True |
| `invoice_cancellation_stock_restore` | heldout | `critic` | `impl_1_marks_cancelled_only.py` | 3 | 2 | 0.67 | True | True |
| `invoice_cancellation_stock_restore` | heldout | `oracle` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `invoice_cancellation_stock_restore` | heldout | `repaired_naive` | `impl_2_correct.py` | 2 | 1 | 0.50 | True | False |
| `invoice_cancellation_stock_restore` | heldout | `repaired_critic` | `impl_2_correct.py` | 2 | 1 | 0.50 | True | False |
| `loyalty_refund_reversal` | development | `naive` | `impl_1_refund_only_no_loyalty.py` | 4 | 3 | 0.75 | True | True |
| `loyalty_refund_reversal` | development | `critic` | `impl_1_refund_only_no_loyalty.py` | 4 | 3 | 0.75 | True | True |
| `loyalty_refund_reversal` | development | `oracle` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `loyalty_refund_reversal` | development | `repaired_naive` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `loyalty_refund_reversal` | development | `repaired_critic` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `payment_webhook_idempotency` | development | `naive` | `impl_1_happy_path_only.py` | 3 | 2 | 0.67 | True | True |
| `payment_webhook_idempotency` | development | `critic` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `payment_webhook_idempotency` | development | `oracle` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `payment_webhook_idempotency` | development | `repaired_naive` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `payment_webhook_idempotency` | development | `repaired_critic` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `rate_limiter_boundary` | development | `naive` | `impl_1_always_allow.py` | 4 | 3 | 0.75 | True | True |
| `rate_limiter_boundary` | development | `critic` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `rate_limiter_boundary` | development | `oracle` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `rate_limiter_boundary` | development | `repaired_naive` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `rate_limiter_boundary` | development | `repaired_critic` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `refund_double_refund` | development | `naive` | `impl_1_naive.py` | 4 | 3 | 0.75 | True | True |
| `refund_double_refund` | development | `critic` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `refund_double_refund` | development | `oracle` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `refund_double_refund` | development | `repaired_naive` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `refund_double_refund` | development | `repaired_critic` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `refund_window_expiry` | development | `naive` | `impl_1_no_window_check.py` | 4 | 3 | 0.75 | True | True |
| `refund_window_expiry` | development | `critic` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `refund_window_expiry` | development | `oracle` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `refund_window_expiry` | development | `repaired_naive` | `impl_2_correct.py` | 2 | 1 | 0.50 | True | False |
| `refund_window_expiry` | development | `repaired_critic` | `impl_2_correct.py` | 2 | 1 | 0.50 | True | False |
| `role_downgrade_session_invalidation` | heldout | `naive` | `impl_1_updates_role_only.py` | 4 | 3 | 0.75 | True | True |
| `role_downgrade_session_invalidation` | heldout | `critic` | `impl_1_updates_role_only.py` | 3 | 2 | 0.67 | True | True |
| `role_downgrade_session_invalidation` | heldout | `oracle` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `role_downgrade_session_invalidation` | heldout | `repaired_naive` | `impl_2_correct.py` | 2 | 1 | 0.50 | True | False |
| `role_downgrade_session_invalidation` | heldout | `repaired_critic` | `impl_2_correct.py` | 2 | 1 | 0.50 | True | False |
| `tenant_isolation_export` | heldout | `naive` | `impl_1_filters_only.py` | 4 | 3 | 0.75 | True | True |
| `tenant_isolation_export` | heldout | `critic` | `impl_1_filters_only.py` | 4 | 3 | 0.75 | True | True |
| `tenant_isolation_export` | heldout | `oracle` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `tenant_isolation_export` | heldout | `repaired_naive` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |
| `tenant_isolation_export` | heldout | `repaired_critic` | `impl_2_correct.py` | 1 | 0 | 0.00 | False | False |

## Interpretation

Incomplete specs do not merely select one bad candidate under a fixed ordering. They admit broader sets of bad-but-public-spec-passing candidates, which means the public spec underconstrains the implementation-selection target.