# Local Repaired Target Summary

| case | expected outcome | actual Dafny outcome | classification | error excerpt | log path |
|---|---|---|---|---|---|
| DA0003 | verify_fail_due_to_repaired_constraint | verify_fail | blocks_bad_candidate | `external_vericoding_cases/candidate_DA0003/dafny_repaired/bad_candidate_repaired_target.dfy(15,17): Warning: This ensures clause is part of a bodyless method. Add the {:axiom} attribute to it or the enclosing method to suppress this warning | 15 | ensures resu` | `results\external_replication\dafny_logs\DA0003_repaired_target_local.log` |
| DA0208 | verify_fail_due_to_repaired_constraint | verify_fail | blocks_bad_candidate | `external_vericoding_cases/candidate_DA0208/dafny_repaired/bad_candidate_repaired_target.dfy(31,19): Warning: This ensures clause is part of a bodyless method. Add the {:axiom} attribute to it or the enclosing method to suppress this warning | 31 | ensures resu` | `results\external_replication\dafny_logs\DA0208_repaired_target_local.log` |
