# Policy-Pack Robustness Evaluation

This report perturbs the policy inventory while keeping the same 36 controlled spec instances fixed. It measures how the Policy Audit Gate trades off dangerous-spec recall against safe-spec allowance and review burden.

## Policy-Pack Robustness

| Policy pack condition | Dangerous allowed | Dangerous caught | Safe allow rate | Exact causal @1 | Exact causal @3 | Review burden |
|---|---:|---:|---:|---:|---:|---:|
| `clean` | 0 | 17 | 78.95% | 6 | 16 | 58.33% |
| `noisy_5x` | 0 | 17 | 78.95% | 6 | 16 | 58.33% |
| `noisy_10x` | 0 | 17 | 78.95% | 6 | 16 | 58.33% |
| `noisy_50x` | 0 | 17 | 78.95% | 6 | 16 | 58.33% |
| `incomplete_25` | 0 | 17 | 78.95% | 5 | 12 | 58.33% |
| `incomplete_50` | 2 | 15 | 78.95% | 3 | 8 | 52.78% |
| `outdated_wording` | 0 | 17 | 0.00% | 9 | 16 | 100.00% |
| `noisy_10x_plus_outdated` | 0 | 17 | 0.00% | 9 | 16 | 100.00% |

## Notes by Condition

- `clean`: Current applicable policy cards.
- `noisy_5x`: Adds 4 irrelevant policy cards for each relevant policy card.
- `noisy_10x`: Adds 9 irrelevant policy cards for each relevant policy card.
- `noisy_50x`: Adds 49 irrelevant policy cards for each relevant policy card.
- `incomplete_25`: Removes the causally relevant omitted policy card for 25% of dangerous cases.
- `incomplete_50`: Removes the causally relevant omitted policy card for 50% of dangerous cases.
- `outdated_wording`: Weakens the wording and keywords of the causally relevant policy card.
- `noisy_10x_plus_outdated`: Adds 9 irrelevant cards per relevant card and weakens the causally relevant policy card.

## Interpretation

Noisy policy packs may legitimately increase conservatism. Incomplete policy packs are expected to miss some dangerous specs because the causally relevant policy is no longer represented. This is a dependency claim, not a bug: the gate targets known-but-omitted policies.