# GPT-5 Nano Spec Inspection

Source: `results/llm_spec_runs.jsonl`
API calls made for this report: `0`
Total `gpt-5-nano` specs inspected: `25`

## Summary

1. Are the nano specs actually weak, or is the coverage checker failing to match them?
   The saved `gpt-5-nano` specs are actually weak for this run: every parsed `public_spec` is empty, so the rule-based checker correctly reports zero clear coverage. This is not primarily a keyword-matching failure.
2. Specs appearing malformed or empty: `25`
3. Specs appearing generic but valid: `0`
4. Specs clearly omitting requirements: `0`
5. Specs appearing semantically useful: `0`

Classification counts:
- `empty`: `25`

## Representative Examples

### Worst nano spec

- task_id: `access_control_delete_user`
- sample_id: `1`
- classification: `empty`
- reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `5`
- unclear_count: `0`

Generated spec:

```text
[EMPTY]
```

### Best nano spec

- task_id: `access_control_delete_user`
- sample_id: `1`
- classification: `empty`
- reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `5`
- unclear_count: `0`

Generated spec:

```text
[EMPTY]
```

### Typical nano spec

- task_id: `expiry_handle_today`
- sample_id: `3`
- classification: `empty`
- reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `5`
- unclear_count: `0`

Generated spec:

```text
[EMPTY]
```

## Per-Spec Inspection

### access_control_delete_user sample 1

- task_id: `access_control_delete_user`
- sample_id: `1`
- quality classification: `empty`
- quality reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `5`
- unclear_count: `0`
- coverage_rate: `0.0`
- first 3 missing requirements:
  - Only admins may delete users (No matching requirement keywords found.)
  - Members and guests must be rejected (No matching requirement keywords found.)
  - Users cannot delete themselves (No matching requirement keywords found.)

Generated spec text:

```text
[EMPTY]
```

Parsed assumptions:
- none

Parsed properties:
- none

Parsed edge cases:
- none

### access_control_delete_user sample 2

- task_id: `access_control_delete_user`
- sample_id: `2`
- quality classification: `empty`
- quality reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `5`
- unclear_count: `0`
- coverage_rate: `0.0`
- first 3 missing requirements:
  - Only admins may delete users (No matching requirement keywords found.)
  - Members and guests must be rejected (No matching requirement keywords found.)
  - Users cannot delete themselves (No matching requirement keywords found.)

Generated spec text:

```text
[EMPTY]
```

Parsed assumptions:
- none

Parsed properties:
- none

Parsed edge cases:
- none

### access_control_delete_user sample 3

- task_id: `access_control_delete_user`
- sample_id: `3`
- quality classification: `empty`
- quality reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `5`
- unclear_count: `0`
- coverage_rate: `0.0`
- first 3 missing requirements:
  - Only admins may delete users (No matching requirement keywords found.)
  - Members and guests must be rejected (No matching requirement keywords found.)
  - Users cannot delete themselves (No matching requirement keywords found.)

Generated spec text:

```text
[EMPTY]
```

Parsed assumptions:
- none

Parsed properties:
- none

Parsed edge cases:
- none

### access_control_delete_user sample 4

- task_id: `access_control_delete_user`
- sample_id: `4`
- quality classification: `empty`
- quality reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `5`
- unclear_count: `0`
- coverage_rate: `0.0`
- first 3 missing requirements:
  - Only admins may delete users (No matching requirement keywords found.)
  - Members and guests must be rejected (No matching requirement keywords found.)
  - Users cannot delete themselves (No matching requirement keywords found.)

Generated spec text:

```text
[EMPTY]
```

Parsed assumptions:
- none

Parsed properties:
- none

Parsed edge cases:
- none

### access_control_delete_user sample 5

- task_id: `access_control_delete_user`
- sample_id: `5`
- quality classification: `empty`
- quality reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `5`
- unclear_count: `0`
- coverage_rate: `0.0`
- first 3 missing requirements:
  - Only admins may delete users (No matching requirement keywords found.)
  - Members and guests must be rejected (No matching requirement keywords found.)
  - Users cannot delete themselves (No matching requirement keywords found.)

Generated spec text:

```text
[EMPTY]
```

Parsed assumptions:
- none

Parsed properties:
- none

Parsed edge cases:
- none

### discount_nonnegative_price sample 1

- task_id: `discount_nonnegative_price`
- sample_id: `1`
- quality classification: `empty`
- quality reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `4`
- unclear_count: `0`
- coverage_rate: `0.0`
- first 3 missing requirements:
  - Price must be non negative (No matching requirement keywords found.)
  - Discount percent must be between 0 and 100 (No matching requirement keywords found.)
  - Final price must never be negative (No matching requirement keywords found.)

Generated spec text:

```text
[EMPTY]
```

Parsed assumptions:
- none

Parsed properties:
- none

Parsed edge cases:
- none

### discount_nonnegative_price sample 2

- task_id: `discount_nonnegative_price`
- sample_id: `2`
- quality classification: `empty`
- quality reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `4`
- unclear_count: `0`
- coverage_rate: `0.0`
- first 3 missing requirements:
  - Price must be non negative (No matching requirement keywords found.)
  - Discount percent must be between 0 and 100 (No matching requirement keywords found.)
  - Final price must never be negative (No matching requirement keywords found.)

Generated spec text:

```text
[EMPTY]
```

Parsed assumptions:
- none

Parsed properties:
- none

Parsed edge cases:
- none

### discount_nonnegative_price sample 3

- task_id: `discount_nonnegative_price`
- sample_id: `3`
- quality classification: `empty`
- quality reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `4`
- unclear_count: `0`
- coverage_rate: `0.0`
- first 3 missing requirements:
  - Price must be non negative (No matching requirement keywords found.)
  - Discount percent must be between 0 and 100 (No matching requirement keywords found.)
  - Final price must never be negative (No matching requirement keywords found.)

Generated spec text:

```text
[EMPTY]
```

Parsed assumptions:
- none

Parsed properties:
- none

Parsed edge cases:
- none

### discount_nonnegative_price sample 4

- task_id: `discount_nonnegative_price`
- sample_id: `4`
- quality classification: `empty`
- quality reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `4`
- unclear_count: `0`
- coverage_rate: `0.0`
- first 3 missing requirements:
  - Price must be non negative (No matching requirement keywords found.)
  - Discount percent must be between 0 and 100 (No matching requirement keywords found.)
  - Final price must never be negative (No matching requirement keywords found.)

Generated spec text:

```text
[EMPTY]
```

Parsed assumptions:
- none

Parsed properties:
- none

Parsed edge cases:
- none

### discount_nonnegative_price sample 5

- task_id: `discount_nonnegative_price`
- sample_id: `5`
- quality classification: `empty`
- quality reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `4`
- unclear_count: `0`
- coverage_rate: `0.0`
- first 3 missing requirements:
  - Price must be non negative (No matching requirement keywords found.)
  - Discount percent must be between 0 and 100 (No matching requirement keywords found.)
  - Final price must never be negative (No matching requirement keywords found.)

Generated spec text:

```text
[EMPTY]
```

Parsed assumptions:
- none

Parsed properties:
- none

Parsed edge cases:
- none

### expiry_handle_today sample 1

- task_id: `expiry_handle_today`
- sample_id: `1`
- quality classification: `empty`
- quality reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `5`
- unclear_count: `0`
- coverage_rate: `0.0`
- first 3 missing requirements:
  - Category lead time must be applied (No matching requirement keywords found.)
  - Items that should have been handled earlier are still handle_today (No matching requirement keywords found.)
  - Already expired items must be handled (No matching requirement keywords found.)

Generated spec text:

```text
[EMPTY]
```

Parsed assumptions:
- none

Parsed properties:
- none

Parsed edge cases:
- none

### expiry_handle_today sample 2

- task_id: `expiry_handle_today`
- sample_id: `2`
- quality classification: `empty`
- quality reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `5`
- unclear_count: `0`
- coverage_rate: `0.0`
- first 3 missing requirements:
  - Category lead time must be applied (No matching requirement keywords found.)
  - Items that should have been handled earlier are still handle_today (No matching requirement keywords found.)
  - Already expired items must be handled (No matching requirement keywords found.)

Generated spec text:

```text
[EMPTY]
```

Parsed assumptions:
- none

Parsed properties:
- none

Parsed edge cases:
- none

### expiry_handle_today sample 3

- task_id: `expiry_handle_today`
- sample_id: `3`
- quality classification: `empty`
- quality reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `5`
- unclear_count: `0`
- coverage_rate: `0.0`
- first 3 missing requirements:
  - Category lead time must be applied (No matching requirement keywords found.)
  - Items that should have been handled earlier are still handle_today (No matching requirement keywords found.)
  - Already expired items must be handled (No matching requirement keywords found.)

Generated spec text:

```text
[EMPTY]
```

Parsed assumptions:
- none

Parsed properties:
- none

Parsed edge cases:
- none

### expiry_handle_today sample 4

- task_id: `expiry_handle_today`
- sample_id: `4`
- quality classification: `empty`
- quality reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `5`
- unclear_count: `0`
- coverage_rate: `0.0`
- first 3 missing requirements:
  - Category lead time must be applied (No matching requirement keywords found.)
  - Items that should have been handled earlier are still handle_today (No matching requirement keywords found.)
  - Already expired items must be handled (No matching requirement keywords found.)

Generated spec text:

```text
[EMPTY]
```

Parsed assumptions:
- none

Parsed properties:
- none

Parsed edge cases:
- none

### expiry_handle_today sample 5

- task_id: `expiry_handle_today`
- sample_id: `5`
- quality classification: `empty`
- quality reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `5`
- unclear_count: `0`
- coverage_rate: `0.0`
- first 3 missing requirements:
  - Category lead time must be applied (No matching requirement keywords found.)
  - Items that should have been handled earlier are still handle_today (No matching requirement keywords found.)
  - Already expired items must be handled (No matching requirement keywords found.)

Generated spec text:

```text
[EMPTY]
```

Parsed assumptions:
- none

Parsed properties:
- none

Parsed edge cases:
- none

### rate_limiter_boundary sample 1

- task_id: `rate_limiter_boundary`
- sample_id: `1`
- quality classification: `empty`
- quality reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `4`
- unclear_count: `0`
- coverage_rate: `0.0`
- first 3 missing requirements:
  - The 6th request must be blocked (No matching requirement keywords found.)
  - The limit is per user, not global (No matching requirement keywords found.)
  - Old requests outside 60 seconds must expire (No matching requirement keywords found.)

Generated spec text:

```text
[EMPTY]
```

Parsed assumptions:
- none

Parsed properties:
- none

Parsed edge cases:
- none

### rate_limiter_boundary sample 2

- task_id: `rate_limiter_boundary`
- sample_id: `2`
- quality classification: `empty`
- quality reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `4`
- unclear_count: `0`
- coverage_rate: `0.0`
- first 3 missing requirements:
  - The 6th request must be blocked (No matching requirement keywords found.)
  - The limit is per user, not global (No matching requirement keywords found.)
  - Old requests outside 60 seconds must expire (No matching requirement keywords found.)

Generated spec text:

```text
[EMPTY]
```

Parsed assumptions:
- none

Parsed properties:
- none

Parsed edge cases:
- none

### rate_limiter_boundary sample 3

- task_id: `rate_limiter_boundary`
- sample_id: `3`
- quality classification: `empty`
- quality reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `4`
- unclear_count: `0`
- coverage_rate: `0.0`
- first 3 missing requirements:
  - The 6th request must be blocked (No matching requirement keywords found.)
  - The limit is per user, not global (No matching requirement keywords found.)
  - Old requests outside 60 seconds must expire (No matching requirement keywords found.)

Generated spec text:

```text
[EMPTY]
```

Parsed assumptions:
- none

Parsed properties:
- none

Parsed edge cases:
- none

### rate_limiter_boundary sample 4

- task_id: `rate_limiter_boundary`
- sample_id: `4`
- quality classification: `empty`
- quality reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `4`
- unclear_count: `0`
- coverage_rate: `0.0`
- first 3 missing requirements:
  - The 6th request must be blocked (No matching requirement keywords found.)
  - The limit is per user, not global (No matching requirement keywords found.)
  - Old requests outside 60 seconds must expire (No matching requirement keywords found.)

Generated spec text:

```text
[EMPTY]
```

Parsed assumptions:
- none

Parsed properties:
- none

Parsed edge cases:
- none

### rate_limiter_boundary sample 5

- task_id: `rate_limiter_boundary`
- sample_id: `5`
- quality classification: `empty`
- quality reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `4`
- unclear_count: `0`
- coverage_rate: `0.0`
- first 3 missing requirements:
  - The 6th request must be blocked (No matching requirement keywords found.)
  - The limit is per user, not global (No matching requirement keywords found.)
  - Old requests outside 60 seconds must expire (No matching requirement keywords found.)

Generated spec text:

```text
[EMPTY]
```

Parsed assumptions:
- none

Parsed properties:
- none

Parsed edge cases:
- none

### refund_double_refund sample 1

- task_id: `refund_double_refund`
- sample_id: `1`
- quality classification: `empty`
- quality reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `4`
- unclear_count: `0`
- coverage_rate: `0.0`
- first 3 missing requirements:
  - Refund must not exceed original payment (No matching requirement keywords found.)
  - Same order cannot be refunded twice (No matching requirement keywords found.)
  - Invalid or cancelled orders must fail (No matching requirement keywords found.)

Generated spec text:

```text
[EMPTY]
```

Parsed assumptions:
- none

Parsed properties:
- none

Parsed edge cases:
- none

### refund_double_refund sample 2

- task_id: `refund_double_refund`
- sample_id: `2`
- quality classification: `empty`
- quality reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `4`
- unclear_count: `0`
- coverage_rate: `0.0`
- first 3 missing requirements:
  - Refund must not exceed original payment (No matching requirement keywords found.)
  - Same order cannot be refunded twice (No matching requirement keywords found.)
  - Invalid or cancelled orders must fail (No matching requirement keywords found.)

Generated spec text:

```text
[EMPTY]
```

Parsed assumptions:
- none

Parsed properties:
- none

Parsed edge cases:
- none

### refund_double_refund sample 3

- task_id: `refund_double_refund`
- sample_id: `3`
- quality classification: `empty`
- quality reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `4`
- unclear_count: `0`
- coverage_rate: `0.0`
- first 3 missing requirements:
  - Refund must not exceed original payment (No matching requirement keywords found.)
  - Same order cannot be refunded twice (No matching requirement keywords found.)
  - Invalid or cancelled orders must fail (No matching requirement keywords found.)

Generated spec text:

```text
[EMPTY]
```

Parsed assumptions:
- none

Parsed properties:
- none

Parsed edge cases:
- none

### refund_double_refund sample 4

- task_id: `refund_double_refund`
- sample_id: `4`
- quality classification: `empty`
- quality reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `4`
- unclear_count: `0`
- coverage_rate: `0.0`
- first 3 missing requirements:
  - Refund must not exceed original payment (No matching requirement keywords found.)
  - Same order cannot be refunded twice (No matching requirement keywords found.)
  - Invalid or cancelled orders must fail (No matching requirement keywords found.)

Generated spec text:

```text
[EMPTY]
```

Parsed assumptions:
- none

Parsed properties:
- none

Parsed edge cases:
- none

### refund_double_refund sample 5

- task_id: `refund_double_refund`
- sample_id: `5`
- quality classification: `empty`
- quality reason: No public_spec, assumptions, properties, or edge_cases were parsed from the model response.
- covered_count: `0`
- missing_count: `4`
- unclear_count: `0`
- coverage_rate: `0.0`
- first 3 missing requirements:
  - Refund must not exceed original payment (No matching requirement keywords found.)
  - Same order cannot be refunded twice (No matching requirement keywords found.)
  - Invalid or cancelled orders must fail (No matching requirement keywords found.)

Generated spec text:

```text
[EMPTY]
```

Parsed assumptions:
- none

Parsed properties:
- none

Parsed edge cases:
- none
