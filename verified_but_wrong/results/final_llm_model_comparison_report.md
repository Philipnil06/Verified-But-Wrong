# Final LLM Model Comparison Report

Source files:
- `results/llm_spec_runs.jsonl`
- `results/llm_model_comparison_latest.json`

API calls made for this report: `0`

## 1. Executive Summary

Deterministic benchmark result:
- Naive specs: `5/5` verified-but-wrong selections.
- Critic specs: `0/5` verified-but-wrong selections.

Live LLM spec experiment:
- `gpt-5.4-mini`: `30` valid specs, average clear coverage rate `0.9467`, exact missing `0`, unclear `7`.
- `gpt-5-nano`: `30` valid specs, average clear coverage rate `0.915`, exact missing `3`, unclear `9`.
- `gpt-5-nano` old invalid empty rows: `25` excluded from metrics.

## 2. Model Comparison Table

| model | valid_specs | invalid_generations | average_clear_coverage_rate | average_possible_coverage_rate | exact_missing_requirements | unclear_requirements | not_clearly_covered_requirements | top not clearly covered categories |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `gpt-5-nano` | 30 | 25 | 0.9150 | 0.9800 | 3 | 9 | 12 | error_behavior_omission: 11, boundary_omission: 6, state_invariant_omission: 5, authorization_omission: 4, security_omission: 4 |
| `gpt-5.4-mini` | 30 | 0 | 0.9467 | 1.0000 | 0 | 7 | 7 | boundary_omission: 7, error_behavior_omission: 7, conservation_omission: 4, invalid_input_omission: 4, domain_rule_omission: 3 |

## 3. Exact Missing Requirements

### 1. gpt-5-nano / access_control_delete_user / sample 3

- model: `gpt-5-nano`
- task_id: `access_control_delete_user`
- sample_id: `3`
- requirement: Members and guests must be rejected
- categories: `authorization_omission`, `error_behavior_omission`, `security_omission`, `state_invariant_omission`
- why marked missing: No matching requirement keywords found.

Generated spec excerpt:

```text
Function: delete_user(target_user_id, requester_user) Purpose: Delete a user account specified by target_user_id. Inputs: - target_user_id: identifier of the user to be deleted. - requester_user: user object of the entity requesting the deletion, including role and user_id. Returns: success boolean or raises error with explicit reason. Behavior: 1) Authoriza...
```

### 2. gpt-5-nano / access_control_delete_user / sample 4

- model: `gpt-5-nano`
- task_id: `access_control_delete_user`
- sample_id: `4`
- requirement: Members and guests must be rejected
- categories: `authorization_omission`, `error_behavior_omission`, `security_omission`, `state_invariant_omission`
- why marked missing: No matching requirement keywords found.

Generated spec excerpt:

```text
Specification for delete_user(entrypoint): Deletes a target user from the system with strict access control. Preconditions: caller is authenticated as a user with role admin. Target_user_id must reference an existing user and must not equal caller's user_id. On success, target user is removed and system state reflects deletion. On failure, no changes occur a...
```

### 3. gpt-5-nano / access_control_delete_user / sample 5

- model: `gpt-5-nano`
- task_id: `access_control_delete_user`
- sample_id: `5`
- requirement: Members and guests must be rejected
- categories: `authorization_omission`, `error_behavior_omission`, `security_omission`, `state_invariant_omission`
- why marked missing: No matching requirement keywords found.

Generated spec excerpt:

```text
Function: delete_user(target_user_id) -> result Purpose: Delete a user account from the system. Only admins may perform deletions. The operation must not allow self-deletion by the requester. All inputs are validated; failures return an error. Behavior: - Preconditions: - The caller must be authenticated as a user and have role 'admin'. Otherwise, the operat...
```


## 4. Unclear Requirements

### 1. gpt-5.4-mini / discount_nonnegative_price / sample 1

- model: `gpt-5.4-mini`
- task_id: `discount_nonnegative_price`
- sample_id: `1`
- requirement: Price must be non negative
- categories: `boundary_omission`, `conservation_omission`, `error_behavior_omission`, `invalid_input_omission`
- why marked unclear: mentions related term(s): price, negative

Generated spec excerpt:

```text
Implement apply_discount(price, discount_percent) to compute a discounted final price. The input price must be non-negative, and discount_percent must be within the inclusive range 0 to 100. The function returns the final price after applying the discount, computed as price * (1 - discount_percent / 100). The returned final price must never be negative; if t...
```

### 2. gpt-5.4-mini / expiry_handle_today / sample 1

- model: `gpt-5.4-mini`
- task_id: `expiry_handle_today`
- sample_id: `1`
- requirement: Already expired items must be handled
- categories: `boundary_omission`, `domain_rule_omission`, `error_behavior_omission`, `temporal_omission`
- why marked unclear: mentions related term(s): already, items, handled

Generated spec excerpt:

```text
Implement should_handle_today(item, today) so that it marks an item as handle_today when the item’s effective handling date is today or earlier. The effective handling date is computed as expiry_date minus category_lead_time_days. If expiry_date is already in the past, the item must still be handled today. The function must reject invalid dates or invalid le...
```

### 3. gpt-5.4-mini / discount_nonnegative_price / sample 1

- model: `gpt-5.4-mini`
- task_id: `discount_nonnegative_price`
- sample_id: `1`
- requirement: Price must be non negative
- categories: `boundary_omission`, `conservation_omission`, `error_behavior_omission`, `invalid_input_omission`
- why marked unclear: mentions related term(s): price, negative

Generated spec excerpt:

```text
Implement apply_discount(price, discount_percent) to compute a discounted final price. The input price must be non-negative. The discount_percent must be within the inclusive range 0 to 100. The function must return a final price that is never negative. Normal behavior: when inputs are valid, return price * (1 - discount_percent / 100). Boundary behavior: pr...
```

### 4. gpt-5.4-mini / discount_nonnegative_price / sample 3

- model: `gpt-5.4-mini`
- task_id: `discount_nonnegative_price`
- sample_id: `3`
- requirement: Price must be non negative
- categories: `boundary_omission`, `conservation_omission`, `error_behavior_omission`, `invalid_input_omission`
- why marked unclear: mentions related term(s): price, negative

Generated spec excerpt:

```text
Implement apply_discount(price, discount_percent) to compute a discounted final price. The input price must be non-negative. The discount_percent must be between 0 and 100 inclusive. The function must return the final price after applying the percentage discount, and the result must never be negative. Normal behavior: a 0% discount returns the original price...
```

### 5. gpt-5.4-mini / discount_nonnegative_price / sample 5

- model: `gpt-5.4-mini`
- task_id: `discount_nonnegative_price`
- sample_id: `5`
- requirement: Price must be non negative
- categories: `boundary_omission`, `conservation_omission`, `error_behavior_omission`, `invalid_input_omission`
- why marked unclear: mentions related term(s): price, negative

Generated spec excerpt:

```text
Implement apply_discount(price, discount_percent) to compute a discounted final price. The input price must be non-negative. The discount_percent must be within the inclusive range 0 to 100. The function must return the final price after applying the discount, using the formula final_price = price * (1 - discount_percent / 100). The returned final price must...
```

### 6. gpt-5.4-mini / expiry_handle_today / sample 1

- model: `gpt-5.4-mini`
- task_id: `expiry_handle_today`
- sample_id: `1`
- requirement: Already expired items must be handled
- categories: `boundary_omission`, `domain_rule_omission`, `error_behavior_omission`, `temporal_omission`
- why marked unclear: mentions related term(s): already, items

Generated spec excerpt:

```text
Implement should_handle_today to determine whether an item must be marked handle_today based on expiry and category lead time. The function must parse and validate the item's expiry_date and category_lead_time_days, and it must fail on any invalid date input. Compute the effective handling threshold as expiry_date minus category_lead_time_days days. Return t...
```

### 7. gpt-5.4-mini / expiry_handle_today / sample 5

- model: `gpt-5.4-mini`
- task_id: `expiry_handle_today`
- sample_id: `5`
- requirement: Already expired items must be handled
- categories: `boundary_omission`, `domain_rule_omission`, `error_behavior_omission`, `temporal_omission`
- why marked unclear: mentions related term(s): already, items, handled

Generated spec excerpt:

```text
Implement should_handle_today(item, today, category_lead_time_days) so that it returns true when the item's handling date has been reached or passed. The handling date is computed as expiry_date minus category_lead_time_days days. If this computed date is equal to today or earlier, the item must be marked/treated as handle_today. Items whose expiry_date is a...
```

### 8. gpt-5-nano / access_control_delete_user / sample 1

- model: `gpt-5-nano`
- task_id: `access_control_delete_user`
- sample_id: `1`
- requirement: Deleted state must be updated
- categories: `authorization_omission`, `error_behavior_omission`, `security_omission`, `state_invariant_omission`
- why marked unclear: mentions related term(s): updated

Generated spec excerpt:

```text
Function: delete_user(target_user_id, requesting_user) -> success/failure Purpose - Delete a user identified by target_user_id from the system. - Access control: only users with role admin may perform deletion. - Self-deletion is forbidden: a user may not delete themselves. - Invalid or missing inputs and non-existent targets must cause failure. Behavior - O...
```

### 9. gpt-5-nano / access_control_delete_user / sample 3

- model: `gpt-5-nano`
- task_id: `access_control_delete_user`
- sample_id: `3`
- requirement: Missing target users must fail
- categories: `authorization_omission`, `error_behavior_omission`, `security_omission`, `state_invariant_omission`
- why marked unclear: mentions related term(s): target, users

Generated spec excerpt:

```text
Function: delete_user(target_user_id, requester_user) Purpose: Delete a user account specified by target_user_id. Inputs: - target_user_id: identifier of the user to be deleted. - requester_user: user object of the entity requesting the deletion, including role and user_id. Returns: success boolean or raises error with explicit reason. Behavior: 1) Authoriza...
```

### 10. gpt-5-nano / discount_nonnegative_price / sample 1

- model: `gpt-5-nano`
- task_id: `discount_nonnegative_price`
- sample_id: `1`
- requirement: Final price must never be negative
- categories: `boundary_omission`, `conservation_omission`, `error_behavior_omission`, `invalid_input_omission`
- why marked unclear: mentions related term(s): final, price, negative

Generated spec excerpt:

```text
Function: apply_discount(price, discount_percent) -> final_price. Preconditions: price >= 0, 0 <= discount_percent <= 100. The function computes final_price = max(0, price * (1 - discount_percent / 100)). If inputs violate preconditions, raise an error clearly describing the violation. Invariants: final_price is always >= 0. Non-destructive behavior: input p...
```

### 11. gpt-5-nano / discount_nonnegative_price / sample 4

- model: `gpt-5-nano`
- task_id: `discount_nonnegative_price`
- sample_id: `4`
- requirement: Final price must never be negative
- categories: `boundary_omission`, `conservation_omission`, `error_behavior_omission`, `invalid_input_omission`
- why marked unclear: mentions related term(s): final, price, negative

Generated spec excerpt:

```text
Specification: apply_discount(price, discount_percent) -> final_price. Valid inputs: price >= 0, 0 <= discount_percent <= 100. Behavior: final_price = max(0, price * (1 - discount_percent/100)). The function must ensure final_price is non-negative. If inputs are invalid, raise an InputError (or similar) or return a failure result. Normal behavior: - Given pr...
```

### 12. gpt-5-nano / expiry_handle_today / sample 1

- model: `gpt-5-nano`
- task_id: `expiry_handle_today`
- sample_id: `1`
- requirement: Items that should have been handled earlier are still handle_today
- categories: `boundary_omission`, `domain_rule_omission`, `error_behavior_omission`, `temporal_omission`
- why marked unclear: mentions related term(s): items, should, handled

Generated spec excerpt:

```text
Spec: should_handle_today(expiry_date, category_lead_time_days) -> bool\n\nDescription: Determine whether an item should be handled today based on expiry_date and a lead time in days. The item should be marked handle_today if expiry_date minus category_lead_time_days is today or in the past. Items that are already expired (expiry_date in the past) must also ...
```

### 13. gpt-5-nano / expiry_handle_today / sample 2

- model: `gpt-5-nano`
- task_id: `expiry_handle_today`
- sample_id: `2`
- requirement: Items that should have been handled earlier are still handle_today
- categories: `boundary_omission`, `domain_rule_omission`, `error_behavior_omission`, `temporal_omission`
- why marked unclear: mentions related term(s): items, should, handled

Generated spec excerpt:

```text
Function entrypoint: should_handle_today(item) -> boolean. Returns true if the item should be marked as handle_today. An item should be marked handle_today if (expiry_date - category_lead_time_days) <= today. Already expired items are also handled. Invalid inputs should raise/return failure.
```

### 14. gpt-5-nano / expiry_handle_today / sample 4

- model: `gpt-5-nano`
- task_id: `expiry_handle_today`
- sample_id: `4`
- requirement: Items that should have been handled earlier are still handle_today
- categories: `boundary_omission`, `domain_rule_omission`, `error_behavior_omission`, `temporal_omission`
- why marked unclear: mentions related term(s): items, should, handled

Generated spec excerpt:

```text
Public spec for entrypoint: should_handle_today Purpose - Determine if an item should be marked as handle_today based on expiry date and category lead time. Entry point - should_handle_today(item, category_lead_time_days) -> boolean Inputs - item: object with at least expiry_date (ISO 8601 date string) and optional id. - category_lead_time_days: integer >= 0...
```

### 15. gpt-5-nano / expiry_handle_today / sample 5

- model: `gpt-5-nano`
- task_id: `expiry_handle_today`
- sample_id: `5`
- requirement: Items that should have been handled earlier are still handle_today
- categories: `boundary_omission`, `domain_rule_omission`, `error_behavior_omission`, `temporal_omission`
- why marked unclear: mentions related term(s): items, should, handled

Generated spec excerpt:

```text
Specification: should_handle_today(item, current_date) Purpose: Determine whether an item should be marked as handle_today based on its expiry date and category lead time. An item should be marked handle_today if (expiry_date - category_lead_time_days) <= today. Items already expired are also marked handle_today. Invalid dates fail. Entrypoint: - should_hand...
```

### 16. gpt-5-nano / refund_double_refund / sample 4

- model: `gpt-5-nano`
- task_id: `refund_double_refund`
- sample_id: `4`
- requirement: Refunded state must be updated after successful refund
- categories: `conservation_omission`, `error_behavior_omission`, `state_invariant_omission`
- why marked unclear: mentions related term(s): refunded, updated, after

Generated spec excerpt:

```text
Public Specification: refund(order_id, amount) -> success/failure with optional refund_id. The function refunds must be positive amounts, never exceed the original payment amount, and only for valid, non-cancelled orders. An order may only be refunded once for a given amount; repeated calls for the same order are allowed only if amount <= remaining_refund_am...
```


## 5. Category Analysis

| category | not clearly covered count |
|---|---:|
| `error_behavior_omission` | 19 |
| `boundary_omission` | 13 |
| `state_invariant_omission` | 6 |
| `authorization_omission` | 5 |
| `security_omission` | 5 |
| `temporal_omission` | 7 |
| `domain_rule_omission` | 7 |
| `conservation_omission` | 7 |
| `invalid_input_omission` | 6 |

Model-level category counts:
- `gpt-5-nano`: {'error_behavior_omission': 11, 'boundary_omission': 6, 'state_invariant_omission': 5, 'authorization_omission': 4, 'security_omission': 4, 'domain_rule_omission': 4, 'temporal_omission': 4, 'conservation_omission': 3, 'invalid_input_omission': 2}
- `gpt-5.4-mini`: {'boundary_omission': 7, 'error_behavior_omission': 7, 'conservation_omission': 4, 'invalid_input_omission': 4, 'domain_rule_omission': 3, 'temporal_omission': 3}

## 6. Interpretation

`gpt-5.4-mini` produced clearer specs than `gpt-5-nano` in this saved experiment: it had a higher average clear coverage rate (`0.9467` vs `0.915`), zero exact missing requirements, and fewer unclear requirements (`7` vs `9`).

`gpt-5-nano` produced more exact omissions and unclear requirements. After the Responses API integration fix, it produced valid visible specifications, but its coverage metrics remain lower than `gpt-5.4-mini` on this small task set.

Even when generated specs are mostly strong, unclear or missing requirements are review targets before a vericoding pipeline trusts the spec. The deterministic benchmark shows why these gaps matter: incomplete public specs can select implementations that pass verification but fail the hidden intent oracle.

## 7. Limitations

- Small synthetic benchmark.
- Rule-based coverage checker.
- Hidden oracles approximate intended behavior.
- LLM-generated specs are not yet automatically compiled into executable tests.
- Old invalid `gpt-5-nano` rows were excluded after the integration fix.
- Results should not be generalized broadly without larger evaluation.

## 8. Recommended Final Wording

1. In the deterministic benchmark, naive incomplete specs selected verified-but-wrong implementations on all five tasks, while omission-aware critic specs eliminated the failure in this task set.
2. In live spec-generation runs, `gpt-5.4-mini` produced the clearest specifications among the tested models, with 30 valid specs, 0 exact missing requirements, and 7 unclear requirements.
3. The model comparison supports the core claim: generated specs can look strong overall while still leaving intent-critical requirements unclear or missing, so spec coverage review should happen before vericoding trusts the spec.