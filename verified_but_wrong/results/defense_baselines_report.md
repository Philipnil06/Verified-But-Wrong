# Defense Baselines Report

| Defense | Dangerous caught | Dangerous allowed | Safe allowed | Safe blocked | Review burden | Needs hidden oracle | Pre-selection deployable |
|---|---:|---:|---:|---:|---:|---|---|
| No audit | 0 | 17 | 19 | 0 | 0 | False | True |
| Keyword-only gate | 7 | 10 | 1 | 0 | 25 | False | True |
| Generic checklist audit | 3 | 14 | 15 | 4 | 0 | False | True |
| Checklist critic only | 5 | 0 | 7 | 0 | 0 | True | False |
| Policy coverage gate | 17 | 0 | 8 | 0 | 28 | False | True |
| Policy Audit Gate | 17 | 0 | 15 | 4 | 12 | False | True |
| Policy Audit Gate + repair | 0 | 0 | 24 | 0 | 0 | False | True |
| Hidden Oracle post-selection | 17 | 0 | 19 | 0 | 0 | True | False |

## Interpretation

The policy audit gate is compared against no audit, generic policy checks, critic-only selection, and hidden-oracle post-selection. Hidden oracles can catch failures after selection, but they are not a pre-selection deployment gate.