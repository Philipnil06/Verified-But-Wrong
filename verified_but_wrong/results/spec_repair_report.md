# Spec Repair Report

Detection alone is not enough. This deterministic repair loop appends policy-card patches and reruns candidate selection using curated requirement tests.

| Spec class | VBW before repair | VBW after repair | Avg patches/spec | Remaining failures |
|---|---:|---:|---:|---:|
| `naive` | 12 | 0 | 3.25 | 0 |
| `critic` | 5 | 0 | 1.25 | 0 |

## Example: loyalty_refund_reversal / naive

- before: `impl_1_refund_only_no_loyalty.py`, VBW=`True`
- after: `impl_2_correct.py`, VBW=`False`
- patches:
  - Invalid or unsupported inputs must return an error and must not mutate state.
  - Successful refunds must reverse any dependent rewards, credits, or loyalty points awarded by the original purchase in proportion to the refunded amount.
  - Loyalty or reward balances must never become negative when refund reversals are applied.
  - Cancelled and chargeback orders must return an error and must not change refund state.

## Example: loyalty_refund_reversal / critic

- before: `impl_1_refund_only_no_loyalty.py`, VBW=`True`
- after: `impl_2_correct.py`, VBW=`False`
- patches:
  - Invalid or unsupported inputs must return an error and must not mutate state.
  - Successful refunds must reverse any dependent rewards, credits, or loyalty points awarded by the original purchase in proportion to the refunded amount.
  - Loyalty or reward balances must never become negative when refund reversals are applied.

## Limitations

- Repair is deterministic text patching, not semantic synthesis.
- Repaired selection uses manually curated requirement-test mappings.
- Generated patch text is never executed as code.