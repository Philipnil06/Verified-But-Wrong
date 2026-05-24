Earlier saved LLM pilot artifacts did not naturally produce verified-but-wrong selections on small tasks. We therefore ran a policy-split spec-writing experiment that better matches the intended deployment concern: product tickets often omit organization policies because those policies live in separate inventories.

| Condition | Valid specs | Causal policy omitted | Selected VBW | Gate caught dangerous | Repair cleared |
|---|---:|---:|---:|---:|---:|
| `ticket_only` | 12 | 0 | 0 | 0 | 5 |
| `ticket_plus_generic_checklist` | 12 | 0 | 0 | 0 | 3 |
| `ticket_plus_retrieved_policy` | 12 | 0 | 0 | 0 | 2 |
| `oracle_full` | 12 | 0 | 0 | 0 | 2 |

One concrete example:
- task: `invoice_cancellation_stock_restore`
- condition: `oracle_full`
- causal policy card: `invoice.cancel.restore_stock`
- policy mention label: `mentioned`
- gate decision: `ALLOW`
- selected candidate before repair: `impl_2_correct.py`
- selected candidate after repair: `impl_2_correct.py`

These runs do not show a stronger omission rate for ticket-only specs than for retrieved-policy specs. That weakens the motivating claim for this particular model/task mix and should be reported directly.

Limitations: this result depends on a small controlled benchmark, rule-based policy mention scoring, and cached API artifacts rather than fresh end-to-end reruns in every reproduction.