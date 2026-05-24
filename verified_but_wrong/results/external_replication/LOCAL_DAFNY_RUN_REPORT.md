# LOCAL_DAFNY_RUN_REPORT

## 1. Environment
- OS/shell: Windows + PowerShell.
- Python: `python` not available, `py -3` = 3.13.0.
- .NET SDK: 8.0.421.
- Dafny: 4.11.0 (`dotnet tool run dafny --version`).
- Z3 status: not in PATH (`z3 --version` fails), but local solver used via `--solver-path .tools/z3/z3-4.12.1-x64-win/bin/z3.exe` for manual direct/repaired runs.
- Probe path: `results/external_replication/local_environment_probe_after_fix.txt`

## 2. Commands run (exact)
- `py -3 --version` -> pass
- `dotnet --version` -> pass
- `dotnet --list-sdks` -> pass
- `dotnet tool list` -> pass
- `dotnet tool run dafny --version` -> pass
- `z3 --version` -> fail (not in PATH)
- `dotnet tool run dafny verify C:\Users\Philip Nilsson\OneDrive - Mälardalens Tekniska Gymnasium\Skrivbordet\Hackathon apartresearch The Secure Program Synthesis\verified_but_wrong\external_vericoding_cases\candidate_DA0003\dafny_direct\bad_candidate.dfy --solver-path C:\Users\Philip Nilsson\OneDrive - Mälardalens Tekniska Gymnasium\Skrivbordet\Hackathon apartresearch The Secure Program Synthesis\verified_but_wrong\.tools\z3\z3-4.12.1-x64-win\bin\z3.exe` -> pass
- `dotnet tool run dafny verify C:\Users\Philip Nilsson\OneDrive - Mälardalens Tekniska Gymnasium\Skrivbordet\Hackathon apartresearch The Secure Program Synthesis\verified_but_wrong\external_vericoding_cases\candidate_DA0157\dafny_direct\bad_candidate.dfy --solver-path C:\Users\Philip Nilsson\OneDrive - Mälardalens Tekniska Gymnasium\Skrivbordet\Hackathon apartresearch The Secure Program Synthesis\verified_but_wrong\.tools\z3\z3-4.12.1-x64-win\bin\z3.exe` -> fail (4)
- `dotnet tool run dafny verify C:\Users\Philip Nilsson\OneDrive - Mälardalens Tekniska Gymnasium\Skrivbordet\Hackathon apartresearch The Secure Program Synthesis\verified_but_wrong\external_vericoding_cases\candidate_DA0208\dafny_direct\bad_candidate.dfy --solver-path C:\Users\Philip Nilsson\OneDrive - Mälardalens Tekniska Gymnasium\Skrivbordet\Hackathon apartresearch The Secure Program Synthesis\verified_but_wrong\.tools\z3\z3-4.12.1-x64-win\bin\z3.exe` -> pass
- `dotnet tool run dafny verify C:\Users\Philip Nilsson\OneDrive - Mälardalens Tekniska Gymnasium\Skrivbordet\Hackathon apartresearch The Secure Program Synthesis\verified_but_wrong\external_vericoding_cases\candidate_DA0003\dafny_repaired\bad_candidate_repaired_target.dfy --solver-path C:\Users\Philip Nilsson\OneDrive - Mälardalens Tekniska Gymnasium\Skrivbordet\Hackathon apartresearch The Secure Program Synthesis\verified_but_wrong\.tools\z3\z3-4.12.1-x64-win\bin\z3.exe` -> fail (4)
- `dotnet tool run dafny verify C:\Users\Philip Nilsson\OneDrive - Mälardalens Tekniska Gymnasium\Skrivbordet\Hackathon apartresearch The Secure Program Synthesis\verified_but_wrong\external_vericoding_cases\candidate_DA0208\dafny_repaired\bad_candidate_repaired_target.dfy --solver-path C:\Users\Philip Nilsson\OneDrive - Mälardalens Tekniska Gymnasium\Skrivbordet\Hackathon apartresearch The Secure Program Synthesis\verified_but_wrong\.tools\z3\z3-4.12.1-x64-win\bin\z3.exe` -> fail (4)
- `py -3 scripts/external_replication/run_intended_examples.py` -> pass
- `py -3 run_external_replication.py` -> pass
- `py -3 scripts/external_replication/make_external_replication_tables.py` -> pass

## 3. Direct-Dafny results table
| case | gap class | command | exit code | verified count | error count | status | log path |
|---|---|---|---:|---:|---:|---|---|
| DA0003 | trivial_postcondition | `dotnet tool run dafny verify C:\Users\Philip Nilsson\OneDrive - Mälardalens Tekniska Gymnasium\Skrivbordet\Hackathon apartresearch The Secure Program Synthesis\verified_but_wrong\external_vericoding_cases\candidate_DA0003\dafny_direct\bad_candidate.dfy --solver-path C:\Users\Philip Nilsson\OneDrive - Mälardalens Tekniska Gymnasium\Skrivbordet\Hackathon apartresearch The Secure Program Synthesis\verified_but_wrong\.tools\z3\z3-4.12.1-x64-win\bin\z3.exe` | 0 | 2 | 0 | direct_dafny_pass | `results\external_replication\dafny_logs\DA0003_original_target_local.log` |
| DA0157 | missing_minimality | `dotnet tool run dafny verify C:\Users\Philip Nilsson\OneDrive - Mälardalens Tekniska Gymnasium\Skrivbordet\Hackathon apartresearch The Secure Program Synthesis\verified_but_wrong\external_vericoding_cases\candidate_DA0157\dafny_direct\bad_candidate.dfy --solver-path C:\Users\Philip Nilsson\OneDrive - Mälardalens Tekniska Gymnasium\Skrivbordet\Hackathon apartresearch The Secure Program Synthesis\verified_but_wrong\.tools\z3\z3-4.12.1-x64-win\bin\z3.exe` | 4 | 1 | 0 | direct_dafny_fail_due_real_spec_strength | `results\external_replication\dafny_logs\DA0157_original_target_local.log` |
| DA0208 | trivial_postcondition | `dotnet tool run dafny verify C:\Users\Philip Nilsson\OneDrive - Mälardalens Tekniska Gymnasium\Skrivbordet\Hackathon apartresearch The Secure Program Synthesis\verified_but_wrong\external_vericoding_cases\candidate_DA0208\dafny_direct\bad_candidate.dfy --solver-path C:\Users\Philip Nilsson\OneDrive - Mälardalens Tekniska Gymnasium\Skrivbordet\Hackathon apartresearch The Secure Program Synthesis\verified_but_wrong\.tools\z3\z3-4.12.1-x64-win\bin\z3.exe` | 0 | 5 | 0 | direct_dafny_pass | `results\external_replication\dafny_logs\DA0208_original_target_local.log` |

## 4. Repaired-target results table
| case | expected outcome | actual Dafny outcome | classification | error excerpt | log path |
|---|---|---|---|---|---|
| DA0003 | verify_fail_due_to_repaired_constraint | verify_fail | blocks_bad_candidate | `external_vericoding_cases/candidate_DA0003/dafny_repaired/bad_candidate_repaired_target.dfy(15,17): Warning: This ensures clause is part of a bodyless method. Add the {:axiom} attribute to it or the enclosing method to suppress this warning | 15 | ensures resu` | `results\external_replication\dafny_logs\DA0003_repaired_target_local.log` |
| DA0208 | verify_fail_due_to_repaired_constraint | verify_fail | blocks_bad_candidate | `external_vericoding_cases/candidate_DA0208/dafny_repaired/bad_candidate_repaired_target.dfy(31,19): Warning: This ensures clause is part of a bodyless method. Add the {:axiom} attribute to it or the enclosing method to suppress this warning | 31 | ensures resu` | `results\external_replication\dafny_logs\DA0208_repaired_target_local.log` |

## 5. Intended examples table
| case | expected outputs | bad candidate outputs | pass/fail | summary path |
|---|---|---|---|---|
| DA0003 | `[13, 28]` | `[0, 0]` | fail | `results/external_replication/intended_examples_summary.jsonl` |
| DA0157 | `[[10, 1, 10], [12, 3, 4]]` | `[[100, 10, 10], [36, 6, 6]]` | fail | `results/external_replication/intended_examples_summary.jsonl` |
| DA0208 | `[5, 10]` | `[0, 0]` | fail | `results/external_replication/intended_examples_summary.jsonl` |

## 6. Updated external replication counts
- high-confidence candidates adjudicated: 41
- Tier 1 direct-Dafny verified passes (local, strict): 2
- Tier 1 repaired-target blocks (local, strict): 2
- Tier 2 adapted demos: 9
- rejected: 7
- deferred: 23
- non-trivial direct-Dafny successes: 0
- non-trivial direct-Dafny failed attempts: 1

## 7. Safe to claim
- Two Tier 1 cases directly verify against reconstructed original benchmark targets while failing intended examples.
- For both Tier 1 cases, the same bad candidate fails after adding the missing target-validity condition.
- DA0157 remains an attempted non-trivial direct-Dafny case and should not be claimed as Tier 1.

## 8. Do not claim
- no prevalence estimate
- no scanner precision over all 128 unless all 128 are adjudicated
- no repaired-target success unless Dafny failed for the intended repaired-target reason
- no DA0157 Tier 1 unless Dafny actually verifies original target

## 9. Run artifacts
- `results/external_replication/full_local_replication_run_after_fix.log`
- `results/external_replication/table_generation_after_fix.log`
- `results/external_replication/local_dafny_direct_summary.{jsonl,csv,md}`
- `results/external_replication/local_repaired_target_summary.{jsonl,csv,md}`
- `results/external_replication/intended_examples_summary.{jsonl,csv,md}`
- `paper_assets/external_replication_summary_table.md`
- `paper_assets/external_replication_cases_table.md`
- `paper_assets/external_replication_repair_table.md`
- `paper_assets/evidence_stack_figure_data.json`
- `paper_assets/evidence_stack_figure.md`
- `paper_assets/evidence_stack_figure.png`
- `paper_assets/evidence_stack_figure.svg`

## 10. Figure 2 numbers (from current figure data)
- Panel A: useful=1448, scanner=128, high=41, inspected=41, validated=11, direct_dafny=2, repaired_blocks=2
