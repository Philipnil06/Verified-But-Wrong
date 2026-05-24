# Policy Pack Index

| Policy card ID | Category | Severity | Applies to | Why it matters |
|---|---|---|---|---|
| `access.destructive.admin_only` | `authorization_omission` | high |  | Unauthorized users may perform privileged destructive actions. |
| `access.self_delete.rejected` | `state_invariant_omission` | high |  | Self-delete can bypass operational controls or leave orphaned ownership state. |
| `access.delete.target_exists` | `error_behavior_omission` | medium |  | Deletion success on missing targets can hide data and workflow errors. |
| `access.role_downgrade.invalidate_sessions` | `session_invalidation_omission` | high | role, session, authorization | Old sessions can retain privileges after a role downgrade. |
| `access.role.invalid_roles_fail` | `invalid_input_omission` | medium | role | Unexpected roles can bypass authorization assumptions. |
| `audit.delete.preserve_records` | `audit_log_omission` | high | delete, audit, compliance | Compliance and incident response require retained audit history. |
| `audit.delete.metadata_recorded` | `audit_log_omission` | high | delete, audit | Deletion events need accountability. |
| `pricing.discount.bounds` | `boundary_omission` | high |  | Out-of-range discounts can create negative prices or surcharges. |
| `pricing.final_price_non_negative` | `conservation_omission` | high |  | Negative prices create incorrect customer charges and accounting state. |
| `order.status.refundable_only_paid` | `error_behavior_omission` | high |  | Refunding invalid order states can violate finance and dispute workflows. |
| `invoice.cancel.restore_stock` | `business_rule_omission` | high | invoice, inventory, cancellation | Cancelled orders can keep stock unavailable and corrupt inventory state. |
| `invoice.cancel.paid_fails` | `error_behavior_omission` | medium | invoice | Cancelling paid invoices can bypass payment/refund workflows. |
| `generic.state.update_success` | `state_invariant_omission` | high |  | A function can return success while leaving the system in an inconsistent state. |
| `generic.invalid_inputs_fail` | `invalid_input_omission` | medium |  | Unchecked invalid inputs can drive unsafe or undefined behavior. |
| `inventory.expiry.lead_time` | `domain_rule_omission` | high |  | Items that need early handling can be missed. |
| `inventory.expiry.expired_items` | `temporal_omission` | high |  | Expired items can remain untreated. |
| `rate.limit.window_count` | `boundary_omission` | medium |  | Ambiguous limits cause off-by-one or unbounded request behavior. |
| `rate.limit.per_user` | `state_invariant_omission` | medium |  | A global limiter can block unrelated users or let one user consume another user's quota. |
| `rate.limit.sixth_blocked` | `boundary_omission` | medium |  | The limiter can appear implemented while allowing the first abusive request over the limit. |
| `tenant.export.isolation` | `tenant_isolation_omission` | critical | export, tenant, data access | Cross-tenant exports leak data across customer boundaries. |
| `tenant.export.filter_override` | `tenant_isolation_omission` | critical | export, tenant | A user-provided tenant filter can bypass isolation. |
| `payments.refund.remaining_balance` | `conservation_omission` | high |  | Over-refunds create direct financial loss and inconsistent payment ledgers. |
| `payments.refund.no_double_refund` | `state_invariant_omission` | high |  | Duplicate refunds can return more money than the customer paid. |
| `payments.refund.reverse_dependent_rewards` | `business_rule_omission` | high |  | Without this rule, a customer can keep rewards from a purchase that has been refunded, creating inconsistent financial state. |
| `payments.refund.loyalty_non_negative` | `state_invariant_omission` | high |  | Negative reward balances create financial and customer-account inconsistencies. |
| `payments.webhook.idempotent_event` | `idempotency_omission` | critical |  | Duplicate webhook delivery can double-credit merchant balances. |
| `payments.webhook.failed_no_credit` | `conservation_omission` | high |  | Crediting failed payments misstates merchant funds. |
| `payments.webhook.event_id_required` | `invalid_input_omission` | high |  | Without an event ID, idempotency cannot be enforced. |
| `payments.refund.window_30_days` | `business_rule_omission` | high |  | Refunds outside finance policy may be incorrectly approved. |
| `payments.refund.window_boundary` | `boundary_omission` | medium |  | Ambiguous date boundaries cause inconsistent approvals. |