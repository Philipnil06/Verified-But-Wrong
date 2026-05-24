# Spec Audit Gate Report

## Purpose

The Spec Audit Gate converts coverage gaps into deployment-style decisions before a vericoding pipeline is allowed to select or accept an implementation.

## Risk Rules

- BLOCK if a critical requirement is exactly missing.
- Pre-selection BLOCK if a critical requirement is exactly missing.
- REVIEW if a critical requirement is unclear.
- REVIEW if clear coverage rate is below 0.90.
- ALLOW if no critical gaps are detected and coverage is above threshold.
- Post-selection BLOCK can additionally be triggered by verified-but-wrong selection; this is for evaluation, not deployment gating.

## Summary by Model

| model | valid specs | invalid specs | ALLOW | REVIEW | BLOCK |
|---|---:|---:|---:|---:|---:|
| `gpt-5-nano` | 40 | 25 | 36 | 4 | 0 |
| `gpt-5.4-mini` | 40 | 0 | 35 | 5 | 0 |

## Per-Task Audit Examples

- pre=`ALLOW` post=`ALLOW` `gpt-5.4-mini` `access_control_delete_user` sample 1: coverage=1.00, selected=impl_2_correct.py
- pre=`ALLOW` post=`ALLOW` `gpt-5.4-mini` `discount_nonnegative_price` sample 1: coverage=1.00, selected=impl_2_correct.py
- pre=`ALLOW` post=`ALLOW` `gpt-5.4-mini` `expiry_handle_today` sample 1: coverage=1.00, selected=impl_2_correct.py
- pre=`ALLOW` post=`ALLOW` `gpt-5.4-mini` `rate_limiter_boundary` sample 1: coverage=1.00, selected=impl_2_correct.py
- pre=`ALLOW` post=`ALLOW` `gpt-5.4-mini` `refund_double_refund` sample 1: coverage=1.00, selected=impl_2_correct.py
- pre=`ALLOW` post=`ALLOW` `gpt-5.4-mini` `access_control_delete_user` sample 1: coverage=1.00, selected=impl_2_correct.py
- pre=`ALLOW` post=`ALLOW` `gpt-5.4-mini` `access_control_delete_user` sample 2: coverage=1.00, selected=impl_2_correct.py
- pre=`ALLOW` post=`ALLOW` `gpt-5.4-mini` `access_control_delete_user` sample 3: coverage=1.00, selected=impl_2_correct.py
- pre=`ALLOW` post=`ALLOW` `gpt-5.4-mini` `access_control_delete_user` sample 4: coverage=1.00, selected=impl_2_correct.py
- pre=`ALLOW` post=`ALLOW` `gpt-5.4-mini` `access_control_delete_user` sample 5: coverage=1.00, selected=impl_2_correct.py
- pre=`ALLOW` post=`ALLOW` `gpt-5.4-mini` `discount_nonnegative_price` sample 1: coverage=1.00, selected=impl_2_correct.py
- pre=`ALLOW` post=`ALLOW` `gpt-5.4-mini` `discount_nonnegative_price` sample 2: coverage=1.00, selected=impl_2_correct.py
- pre=`ALLOW` post=`ALLOW` `gpt-5.4-mini` `discount_nonnegative_price` sample 3: coverage=1.00, selected=impl_2_correct.py
- pre=`ALLOW` post=`ALLOW` `gpt-5.4-mini` `discount_nonnegative_price` sample 4: coverage=1.00, selected=impl_2_correct.py
- pre=`ALLOW` post=`ALLOW` `gpt-5.4-mini` `discount_nonnegative_price` sample 5: coverage=1.00, selected=impl_2_correct.py
- pre=`ALLOW` post=`ALLOW` `gpt-5.4-mini` `expiry_handle_today` sample 1: coverage=1.00, selected=impl_2_correct.py
- pre=`ALLOW` post=`ALLOW` `gpt-5.4-mini` `expiry_handle_today` sample 2: coverage=1.00, selected=impl_2_correct.py
- pre=`ALLOW` post=`ALLOW` `gpt-5.4-mini` `expiry_handle_today` sample 3: coverage=1.00, selected=impl_2_correct.py
- pre=`ALLOW` post=`ALLOW` `gpt-5.4-mini` `expiry_handle_today` sample 4: coverage=1.00, selected=impl_2_correct.py
- pre=`ALLOW` post=`ALLOW` `gpt-5.4-mini` `expiry_handle_today` sample 5: coverage=1.00, selected=impl_2_correct.py

## Example BLOCK Decision

No saved audit example was available for this decision level.

## Example REVIEW Decision

- task: `payment_webhook_idempotency`
- model: `gpt-5.4-mini`
- sample: `1`
- pre-selection decision: `REVIEW`
- post-selection decision: `REVIEW`
- recommendation: Require review or spec repair before trusting this spec for selection.
- CI exit code: `1`
- unclear requirements:
  - Payment webhook events must include a non-empty event_id. (invalid_input_omission)

## Example ALLOW Decision

- task: `access_control_delete_user`
- model: `gpt-5.4-mini`
- sample: `1`
- pre-selection decision: `ALLOW`
- post-selection decision: `ALLOW`
- recommendation: No critical policy gaps detected by this audit gate; selection may proceed.
- CI exit code: `0`

## CI/CD Use

A CI job can run this gate before implementation selection. `ALLOW` permits selection, `REVIEW` escalates to a human/spec-repair step, and `BLOCK` prevents a spec-driven pipeline from verifying the wrong target.