# LLM Not Clearly Covered Requirements Report

Model: `gpt-5.4-mini`
Total specs: `25`
Average coverage rate: `0.9540000000000001`
Total not clearly covered requirements: `5`

Note: all five not-clearly-covered items in this saved run were classified as `unclear`; there were zero items with status exactly `missing`. Unclear means the generated spec may have covered the requirement semantically, but did not match the stricter rule-based coverage patterns. These are review targets, not confirmed omissions.

## 1. discount_nonnegative_price sample 1

- task_id: `discount_nonnegative_price`
- sample_id: `1`
- coverage status: `unclear`
- not clearly covered requirement: Price must be non negative
- not clearly covered categories: `boundary_omission`, `conservation_omission`, `error_behavior_omission`, `invalid_input_omission`
- why marked not clearly covered: mentions related term(s): price, negative

Generated spec excerpt:

```text
Implement apply_discount(price, discount_percent) to compute a discounted final price. The input price must be non-negative. The discount_percent must be within the inclusive range 0 to 100. The function must return a final price that is never negative. Normal behavior: when inputs are valid, return price * (1 - discount_percent / 100). Boundary behavior: price = 0 returns 0 for any valid discount_percent; discount_percent = 0 returns the original price; discount_percent = 100 returns 0. Invalid input behavior: if ...
```

## 2. discount_nonnegative_price sample 3

- task_id: `discount_nonnegative_price`
- sample_id: `3`
- coverage status: `unclear`
- not clearly covered requirement: Price must be non negative
- not clearly covered categories: `boundary_omission`, `conservation_omission`, `error_behavior_omission`, `invalid_input_omission`
- why marked not clearly covered: mentions related term(s): price, negative

Generated spec excerpt:

```text
Implement apply_discount(price, discount_percent) to compute a discounted final price. The input price must be non-negative. The discount_percent must be between 0 and 100 inclusive. The function must return the final price after applying the percentage discount, and the result must never be negative. Normal behavior: a 0% discount returns the original price; a 100% discount returns 0; intermediate values reduce the price proportionally. Boundary behavior: price = 0 is valid and always returns 0; discount_percent =...
```

## 3. discount_nonnegative_price sample 5

- task_id: `discount_nonnegative_price`
- sample_id: `5`
- coverage status: `unclear`
- not clearly covered requirement: Price must be non negative
- not clearly covered categories: `boundary_omission`, `conservation_omission`, `error_behavior_omission`, `invalid_input_omission`
- why marked not clearly covered: mentions related term(s): price, negative

Generated spec excerpt:

```text
Implement apply_discount(price, discount_percent) to compute a discounted final price. The input price must be non-negative. The discount_percent must be within the inclusive range 0 to 100. The function must return the final price after applying the discount, using the formula final_price = price * (1 - discount_percent / 100). The returned final price must never be negative; if the calculated result would be below zero due to numeric representation or rounding, it must be clamped to 0.0 or the equivalent zero val...
```

## 4. expiry_handle_today sample 1

- task_id: `expiry_handle_today`
- sample_id: `1`
- coverage status: `unclear`
- not clearly covered requirement: Already expired items must be handled
- not clearly covered categories: `boundary_omission`, `domain_rule_omission`, `error_behavior_omission`, `temporal_omission`
- why marked not clearly covered: mentions related term(s): already, items

Generated spec excerpt:

```text
Implement should_handle_today to determine whether an item must be marked handle_today based on expiry and category lead time. The function must parse and validate the item's expiry_date and category_lead_time_days, and it must fail on any invalid date input. Compute the effective handling threshold as expiry_date minus category_lead_time_days days. Return true when the threshold date is today or earlier in the system's current date context. Items whose expiry_date is already in the past must also return true, even...
```

## 5. expiry_handle_today sample 5

- task_id: `expiry_handle_today`
- sample_id: `5`
- coverage status: `unclear`
- not clearly covered requirement: Already expired items must be handled
- not clearly covered categories: `boundary_omission`, `domain_rule_omission`, `error_behavior_omission`, `temporal_omission`
- why marked not clearly covered: mentions related term(s): already, items, handled

Generated spec excerpt:

```text
Implement should_handle_today(item, today, category_lead_time_days) so that it returns true when the item's handling date has been reached or passed. The handling date is computed as expiry_date minus category_lead_time_days days. If this computed date is equal to today or earlier, the item must be marked/treated as handle_today. Items whose expiry_date is already in the past must also be handled. If the item is not yet within the lead-time window, it must not be marked handle_today. Invalid dates must fail determi...
```
