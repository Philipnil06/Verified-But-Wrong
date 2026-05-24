# External Issue Suite Evaluation

This suite uses externally sourced public issue patterns adapted into minimal vericoding-style cases. These are not bug reproductions and not prevalence estimates.

| Case | Public source | Omitted policy | Before repair VBW | Gate | After repair |
|---|---|---|---|---|---|
| `kibana_role_downgrade_session_invalidation` | https://github.com/elastic/kibana/issues/192346 | auth.role_downgrade.session_invalidation | yes | `BLOCK` | cleared |
| `prisma_tenant_isolation_export` | https://github.com/prisma/prisma/issues/12420 | tenant.export.isolation, tenant.export.filter_override | yes | `REVIEW` | cleared |
| `vendure_invoice_cancellation_stock_restore` | https://github.com/vendure-ecommerce/vendure/issues/91 | invoice.cancel.restore_stock, invoice.cancel.paid_fails | yes | `REVIEW` | cleared |
| `woocommerce_payment_webhook_idempotency` | https://github.com/woocommerce/woocommerce-gateway-stripe/issues/2339 | payments.webhook.idempotent_event, payments.webhook.event_id_required | yes | `REVIEW` | cleared |

## Framing

- externally sourced adapted issue suite
- public software issue patterns
- not bug reproductions
- toy candidates and hidden oracles are authored for evaluation