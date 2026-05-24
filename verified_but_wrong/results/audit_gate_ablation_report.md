# Audit Gate Ablation Report

| Gate variant | Dangerous allowed | Dangerous catch rate | Safe allow rate | Review burden | Failure mode |
|---|---:|---:|---:|---:|---|
| `allow_all` | 17 | 0.0000 | 1.0000 | 0 | allows dangerous specs |
| `keyword_only` | 0 | 1.0000 | 0.4211 | 28 | review/block burden |
| `policy_cards_no_severity` | 0 | 1.0000 | 0.4211 | 28 | review/block burden |
| `severity_only` | 0 | 1.0000 | 0.7895 | 21 | review/block burden |
| `category_only` | 10 | 0.4118 | 0.7895 | 0 | allows dangerous specs |
| `no_unclear_handling` | 10 | 0.4118 | 0.7895 | 0 | allows dangerous specs |
| `no_business_rule_cards` | 3 | 0.8235 | 0.5263 | 0 | allows dangerous specs |
| `generic_policy_only` | 14 | 0.1765 | 0.7895 | 0 | allows dangerous specs |
| `task_policy_with_severity` | 0 | 1.0000 | 0.7895 | 12 | review/block burden |
| `full_policy_audit_gate` | 0 | 1.0000 | 0.7895 | 12 | review/block burden |

## Interpretation

The ablation compares trivial and weaker gates with the full policy audit gate. Review burden is reported explicitly rather than hidden.