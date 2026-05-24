# Refund Window Hard-Mode Report

## Deterministic Result

- Naive public spec selects `impl_1_no_window_check.py` and is verified-but-wrong.
- Critic public spec selects `impl_2_correct.py` and passes the hidden oracle.

## LLM Generated Spec Coverage

| model | valid specs | exact missing 30-day window | unclear 30-day window | exact missing manual_override | exact missing day30/day31 boundary | did not clearly mention refund window |
|---|---:|---:|---:|---:|---:|---:|
| `gpt-5.4-mini` | 5 | 0 | 1 | 0 | 0 | 1 |
| `gpt-5-nano` | 5 | 0 | 0 | 0 | 1 | 0 |

## LLM Spec -> Selection Result

| model | verified_but_wrong_count | hidden_oracle_pass_rate | selected candidates |
|---|---:|---:|---|
| `gpt-5.4-mini` | 0 | 1.0000 | {'impl_2_correct.py': 5} |
| `gpt-5-nano` | 0 | 1.0000 | {'impl_2_correct.py': 5} |

## Verified-But-Wrong Live Examples

No live verified-but-wrong examples were found for the saved refund-window LLM specs. The generated specs selected candidates that passed the hidden oracle in this harness.

## Interesting Generated Spec Excerpts

### gpt-5.4-mini sample 5
- refund window status: `unclear` (mentions related term(s): refunds, allowed, within)
- manual_override status: `covered` (manual_override, manual override, override)
- day30/day31 boundary status: `covered` (day 30, inclusive)

```text
Function process_refund SHALL create a refund only for paid orders when all eligibility rules pass. A refund request MUST specify a positive refund amount. The amount MUST be less than or equal to the order’s remaining refundable paid amount (paid amount minus refunded_total). Orders in status cancelled or chargeback MUST be rejected as non-refundable. By default, refunds are allowed only if the refund is requested within 30 calendar days of the order purchase timestamp; requests after this window MUST be rejected unless a manual_override flag or equivalent authorization override is present. On success, process_refund MUST persistently increment refunded_total by the refunded amount and MUST preserve the invariant that refunded_total never exceeds the original paid amount. The function MUS...
```

### gpt-5-nano sample 1
- refund window status: `covered` (30 days, within 30 days, purchase date)
- manual_override status: `covered` (manual_override, manual override, override)
- day30/day31 boundary status: `covered` (more than 30 days, boundary)

```text
Specification: process_refund(order_id, amount, requester) -> Result Purpose: Determine refund eligibility for paid orders and update refund state accordingly. Inputs - order_id: identifier of a paid order subject to refund. - amount: positive numeric value representing the refund amount to issue. - requester: identity/credentials of the caller (for authorization checks). Outputs - Success: refund is processed; refunded_total updated; order state may be updated to reflect refund. - Failure: refund is rejected with reason; no state mutated. Normal behavior 1. Eligibility checks - The order exists and is in a paid state (not canceled/chargeback). - amount > 0. - amount <= remaining_paid_amount, where remaining_paid_amount = total_paid_amount - refunded_total. - If the order purchase date is ...
```

## Limitations

- The 30-day rule is present in the natural language intent but not overemphasized.
- Coverage classification is rule-based.
- Requirement-to-test mapping is manually curated.
- This is a controlled harness, not an automatic spec compiler.
- No LLM-generated text is executed as code.