# Policy Gate Threshold Sweep

| Gate profile | Dangerous allowed | Dangerous caught | Safe allow rate | Review burden | Safe blocked |
|---|---:|---:|---:|---:|---:|
| `conservative` | 0 | 17 | 0.4211 | 5 | 9 |
| `default` | 0 | 17 | 0.7895 | 12 | 4 |
| `permissive` | 10 | 7 | 0.7895 | 11 | 0 |

The default profile is selected because it preserves zero dangerous escapes in the current controlled/heldout suite while allowing most safe specs.