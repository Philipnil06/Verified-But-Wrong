# LLM Policy-Split Evaluation

- status: `partial_cached_coverage`
- live API calls run: `0`
- cache hits used: `48`
- model: `gpt-5-nano`
- provider: `openai_compatible`
- requested runs: `144`
- completed runs: `48`
- valid specs: `48`

| Condition | Valid specs | Causal policy omitted | Selected VBW | Gate caught dangerous | Repair cleared |
|---|---:|---:|---:|---:|---:|
| `ticket_only` | 12 | 0 | 0 | 0 | 5 |
| `ticket_plus_generic_checklist` | 12 | 0 | 0 | 0 | 3 |
| `ticket_plus_retrieved_policy` | 12 | 0 | 0 | 0 | 2 |
| `oracle_full` | 12 | 0 | 0 | 0 | 2 |

## Per-Task Table

| Task | Condition | Valid specs | Causal policy omitted | Selected VBW | Gate decisions | Repair cleared |
|---|---|---:|---:|---:|---|---:|
| `access_control_delete_user` | `ticket_only` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `audit_log_retention_delete_user` | `ticket_only` | 1 | 0 | 0 | REVIEW:1 | 1 |
| `discount_nonnegative_price` | `ticket_only` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `expiry_handle_today` | `ticket_only` | 1 | 0 | 0 | REVIEW:1 | 1 |
| `invoice_cancellation_stock_restore` | `ticket_only` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `loyalty_refund_reversal` | `ticket_only` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `payment_webhook_idempotency` | `ticket_only` | 1 | 0 | 0 | REVIEW:1 | 1 |
| `rate_limiter_boundary` | `ticket_only` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `refund_double_refund` | `ticket_only` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `refund_window_expiry` | `ticket_only` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `role_downgrade_session_invalidation` | `ticket_only` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `tenant_isolation_export` | `ticket_only` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `access_control_delete_user` | `ticket_plus_generic_checklist` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `audit_log_retention_delete_user` | `ticket_plus_generic_checklist` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `discount_nonnegative_price` | `ticket_plus_generic_checklist` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `expiry_handle_today` | `ticket_plus_generic_checklist` | 1 | 0 | 0 | REVIEW:1 | 1 |
| `invoice_cancellation_stock_restore` | `ticket_plus_generic_checklist` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `loyalty_refund_reversal` | `ticket_plus_generic_checklist` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `payment_webhook_idempotency` | `ticket_plus_generic_checklist` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `rate_limiter_boundary` | `ticket_plus_generic_checklist` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `refund_double_refund` | `ticket_plus_generic_checklist` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `refund_window_expiry` | `ticket_plus_generic_checklist` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `role_downgrade_session_invalidation` | `ticket_plus_generic_checklist` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `tenant_isolation_export` | `ticket_plus_generic_checklist` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `access_control_delete_user` | `ticket_plus_retrieved_policy` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `audit_log_retention_delete_user` | `ticket_plus_retrieved_policy` | 1 | 0 | 0 | REVIEW:1 | 1 |
| `discount_nonnegative_price` | `ticket_plus_retrieved_policy` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `expiry_handle_today` | `ticket_plus_retrieved_policy` | 1 | 0 | 0 | REVIEW:1 | 1 |
| `invoice_cancellation_stock_restore` | `ticket_plus_retrieved_policy` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `loyalty_refund_reversal` | `ticket_plus_retrieved_policy` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `payment_webhook_idempotency` | `ticket_plus_retrieved_policy` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `rate_limiter_boundary` | `ticket_plus_retrieved_policy` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `refund_double_refund` | `ticket_plus_retrieved_policy` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `refund_window_expiry` | `ticket_plus_retrieved_policy` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `role_downgrade_session_invalidation` | `ticket_plus_retrieved_policy` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `tenant_isolation_export` | `ticket_plus_retrieved_policy` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `access_control_delete_user` | `oracle_full` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `audit_log_retention_delete_user` | `oracle_full` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `discount_nonnegative_price` | `oracle_full` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `expiry_handle_today` | `oracle_full` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `invoice_cancellation_stock_restore` | `oracle_full` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `loyalty_refund_reversal` | `oracle_full` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `payment_webhook_idempotency` | `oracle_full` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `rate_limiter_boundary` | `oracle_full` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `refund_double_refund` | `oracle_full` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `refund_window_expiry` | `oracle_full` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `role_downgrade_session_invalidation` | `oracle_full` | 1 | 0 | 0 | ALLOW:1 | 1 |
| `tenant_isolation_export` | `oracle_full` | 1 | 0 | 0 | ALLOW:1 | 1 |

## Cautious Interpretation

These runs do not show a stronger omission rate for ticket-only specs than for retrieved-policy specs. That weakens the motivating claim for this particular model/task mix and should be reported directly.

## Limitations

- The benchmark has 12 small controlled tasks rather than a production ticket corpus.
- Policy mention scoring combines exact keywords, related terms, and gate classification; disagreements are marked ambiguous rather than forced into a binary label.
- Candidate selection and repair rely on curated executable requirement tests and deterministic text patching.
- No live API call is made during `run_all_repro.py`; cached artifacts are required for paper-ready quantitative evidence in default reproduction.