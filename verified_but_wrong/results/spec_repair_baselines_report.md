# Spec Repair Baselines Report

| Repair method | Naive VBW after repair | Critic VBW after repair | Avg patches/spec | Notes |
|---|---:|---:|---:|---|
| `no_repair` | 12 | 5 | 0.00 | deterministic baseline |
| `generic_repair` | 11 | 5 | 1.00 | deterministic baseline |
| `checklist_repair` | 10 | 5 | 1.00 | deterministic baseline |
| `policy_targeted_repair` | 0 | 0 | 2.25 | deterministic baseline |
| `oracle_repair` | 0 | 0 | 1.00 | upper bound |

## Loyalty Case Study

| Stage | VBW after | Selected |
|---|---:|---|
| `no_repair` | True | `impl_1_refund_only_no_loyalty.py` |
| `generic_repair` | True | `impl_1_refund_only_no_loyalty.py` |
| `checklist_repair` | True | `impl_1_refund_only_no_loyalty.py` |
| `policy_targeted_repair` | False | `impl_2_correct.py` |
| `oracle_repair` | False | `impl_2_correct.py` |