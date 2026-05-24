# Policy Gate Calibration Report

This report evaluates the deployable pre-selection policy audit gate. The gate sees public spec text and policy packs, not hidden oracle outcomes.

## Summary Metrics

- dangerous_total: 17
- dangerous_allowed: 0
- dangerous_caught: 17
- dangerous_catch_rate: 1.0000
- safe_total: 19
- safe_allowed: 15
- safe_allow_rate: 0.7895
- false_allow_count: 0
- false_block_count: 4
- review_burden_count: 12
- high_or_critical_dangerous_catch_rate: 1.0000

## Confusion Matrix

| Ground truth / Gate decision | ALLOW | REVIEW | BLOCK |
|---|---:|---:|---:|
| Dangerous specs | 0 | 12 | 5 |
| Safe specs | 15 | 0 | 4 |

## Per-Mode Table

| Spec class | Count | Dangerous | ALLOW | REVIEW | BLOCK | Dangerous allowed | Safe blocked |
|---|---:|---:|---:|---:|---:|---:|---:|
| `naive` | 12 | 12 | 0 | 8 | 4 | 0 | 0 |
| `critic` | 12 | 5 | 5 | 4 | 3 | 0 | 2 |
| `oracle` | 12 | 0 | 10 | 0 | 2 | 0 | 2 |

## Interpretation

The policy audit gate does not simply use the hidden oracle. It compares public specs against policy-pack cards. Safe specs can still be reviewed if policy language is unclear, which is reported as review burden rather than hidden as success.

## Limitations

- Controlled calibration, not a general guarantee.
- Policy cards are benchmark-supplied requirement inventories.
- Keyword coverage is deterministic and auditable but not semantic proof.