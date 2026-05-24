# Updated Paper Tables

## Candidate-Set Underconstraint

| Spec mode | Mean underconstraint risk | Tasks with existence risk | Selected VBW |
|---|---:|---:|---:|
| `naive` | 0.74 | 12/12 | 12/12 |
| `critic` | 0.29 | 5/12 | 5/12 |
| `oracle` | 0.00 | 0/12 | 0/12 |
| `repaired_naive` | 0.25 | 6/12 | 0/12 |
| `repaired_critic` | 0.25 | 6/12 | 0/12 |

## LLM Policy-Split

| Condition | Valid specs | Causal policy omitted | Selected VBW | Gate caught dangerous | Repair cleared |
|---|---:|---:|---:|---:|---:|
| `ticket_only` | 12 | 0 | 0 | 0 | 5 |
| `ticket_plus_generic_checklist` | 12 | 0 | 0 | 0 | 3 |
| `ticket_plus_retrieved_policy` | 12 | 0 | 0 | 0 | 2 |
| `oracle_full` | 12 | 0 | 0 | 0 | 2 |

## Formal Demo

Formal demo status: `skipped_dafny_not_installed`.