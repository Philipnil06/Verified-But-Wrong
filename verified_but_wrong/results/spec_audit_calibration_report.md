# Spec Audit Gate Calibration Report

## Executive Summary

- total controlled specs audited: 24
- verified-but-wrong specs: 9
- pre-selection gate allowed verified-but-wrong specs: 0
- pre-selection gate caught verified-but-wrong specs: 9
- wrong selection catch rate: 1.0000
- review/block burden on non-wrong specs: 4 (0.2667)

Pre-selection audit allowed 0 verified-but-wrong specs in the controlled benchmark.

## Table By Mode

| mode | specs audited | verified_but_wrong_count | pre_ALLOW | pre_REVIEW | pre_BLOCK | allowed_verified_but_wrong_count | caught_verified_but_wrong_count |
|---|---:|---:|---:|---:|---:|---:|---:|
| `naive` | 8 | 8 | 0 | 5 | 3 | 0 | 8 |
| `critic` | 8 | 1 | 5 | 1 | 2 | 0 | 1 |
| `oracle` | 8 | 0 | 6 | 0 | 2 | 0 | 0 |

## Critical Example: Naive Spec Caught Before Wrong Selection

- task_id: `access_control_delete_user`
- mode: `naive`
- spec excerpt: The function should delete a target user.
- pre_selection_decision: `BLOCK`
- selected candidate: `impl_1_no_auth.py`
- verified_but_wrong: `True`
- explanation: The incomplete public spec was escalated before it could safely be used for implementation selection.
- missing/unclear critical requirements:
  - Successful state-changing operations must update the relevant persisted state or ledger field. (state_invariant_omission)
  - Only admins may perform destructive user actions such as deleting users. (authorization_omission)

## Critical Example: Loyalty Critic Caught Before Wrong Selection

- task_id: `loyalty_refund_reversal`
- mode: `critic`
- spec excerpt: Refund amounts must be positive and cannot exceed the remaining paid amount. Only paid orders can be refunded. Successful refunds must update refunded_total and cannot exceed the original payment.
- pre_selection_decision: `REVIEW`
- selected candidate: `impl_1_refund_only_no_loyalty.py`
- verified_but_wrong: `True`
- explanation: The checklist critic missed an organization-specific business rule, and the pre-selection gate escalated it.
- missing/unclear critical requirements:
  - If a refund reverses a purchase that awarded loyalty points, credits, or rewards, the refunded portion must reverse the corresponding dependent value. (business_rule_omission)
  - Refund-related loyalty or reward reversal must not make the customer reward balance negative. (state_invariant_omission)

## Critical Example: Oracle Spec Allowed And Correct

- task_id: `discount_nonnegative_price`
- mode: `oracle`
- spec excerpt: Apply a discount only when price is non negative and discount percent is between 0 and 100. The final price must never be negative.
- pre_selection_decision: `ALLOW`
- selected candidate: `impl_2_correct.py`
- verified_but_wrong: `False`
- explanation: The full intended spec covered the benchmark requirements and selected an implementation that passed the hidden oracle.
- missing/unclear critical requirements:
  - none

## Safety-Gate Metric

- allowed_wrong_selection_count: 0
- wrong_selection_catch_rate: 1.0000

## Saved LLM Spec Audit Calibration

In the saved LLM pilot suite, specs allowed by the gate produced 0 verified-but-wrong selections.

| model | valid specs | ALLOW | REVIEW | BLOCK | verified_but_wrong | ALLOW + verified_but_wrong | hidden pass rate for ALLOW |
|---|---:|---:|---:|---:|---:|---:|---:|
| `gpt-5-nano` | 40 | 36 | 4 | 0 | 0 | 0 | 1.0000 |
| `gpt-5.4-mini` | 40 | 35 | 5 | 0 | 0 | 0 | 1.0000 |

## Limitations

- This is calibrated on controlled benchmark specs.
- Requirement coverage uses known benchmark requirements.
- In real deployments, requirement discovery remains hard.
- The audit gate is a safety layer, not a proof of correctness.