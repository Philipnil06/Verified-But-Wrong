# Final LLM Spec to Selection Report

This report is built from saved LLM-generated specs only. No LLM spec text is executed as code.

## Summary by Model

| model | valid_specs | invalid_specs | verified_but_wrong_count | verified_but_wrong_rate | hidden_oracle_pass_rate | avg selected requirements |
|---|---:|---:|---:|---:|---:|---:|
| `gpt-5-nano` | 40 | 25 | 0 | 0.0000 | 1.0000 | 4.90 |
| `gpt-5.4-mini` | 40 | 0 | 0 | 0.0000 | 1.0000 | 4.92 |

## Wrong Selection Examples

No verified-but-wrong selections were found in the saved LLM selection experiment.

## Correct Selection Examples

### gpt-5.4-mini / access_control_delete_user / sample 1

- selected candidate: `impl_2_correct.py`
- selected requirements: 6
- hidden oracle passed: `True`

### gpt-5.4-mini / discount_nonnegative_price / sample 1

- selected candidate: `impl_2_correct.py`
- selected requirements: 4
- hidden oracle passed: `True`

### gpt-5.4-mini / expiry_handle_today / sample 1

- selected candidate: `impl_2_correct.py`
- selected requirements: 5
- hidden oracle passed: `True`

### gpt-5.4-mini / rate_limiter_boundary / sample 1

- selected candidate: `impl_2_correct.py`
- selected requirements: 5
- hidden oracle passed: `True`

### gpt-5.4-mini / refund_double_refund / sample 1

- selected candidate: `impl_2_correct.py`
- selected requirements: 5
- hidden oracle passed: `True`

### gpt-5.4-mini / access_control_delete_user / sample 1

- selected candidate: `impl_2_correct.py`
- selected requirements: 6
- hidden oracle passed: `True`

### gpt-5.4-mini / access_control_delete_user / sample 2

- selected candidate: `impl_2_correct.py`
- selected requirements: 6
- hidden oracle passed: `True`

### gpt-5.4-mini / access_control_delete_user / sample 3

- selected candidate: `impl_2_correct.py`
- selected requirements: 6
- hidden oracle passed: `True`

### gpt-5.4-mini / access_control_delete_user / sample 4

- selected candidate: `impl_2_correct.py`
- selected requirements: 6
- hidden oracle passed: `True`

### gpt-5.4-mini / access_control_delete_user / sample 5

- selected candidate: `impl_2_correct.py`
- selected requirements: 6
- hidden oracle passed: `True`


## Limitations

- The requirement-to-test mapping is manually curated.
- Coverage classification is rule-based.
- This is a controlled harness, not a fully automatic spec compiler.
- Hidden oracles approximate intended behavior.
- LLM-generated specs are mapped to pre-written executable tests; generated text is never executed as code.