# External Vericoding Benchmark Audit

## Validated case table

| Case | Source | Gap category | NL intent | Formal spec gap | Bad candidate | Demo type | Adapted spec check | Intended examples | VBW demo |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DA0003 |  | trivial_postcondition | Return the maximum total chocolates under red/blue divisibility rules and choose the better reward when divisible by both. | Formal target for solve only ensures result >= 0 and does not encode optimization or divisibility counting semantics. | Always return 0. | fully_executable | True | False | True |
| DA0010 |  | simulation_semantics_missing | Simulate pouring and overflow split through the pyramid and count fully filled glasses after t seconds. | Formal target constrains result bounds plus selected edge conditions, without encoding full per-step flow semantics. | Return 0 for t=0 and 1 otherwise, ignoring simulation. | fully_executable | True | False | True |
| DA0157 |  | optimization_missing | Find minimum possible area (and corresponding dimensions) meeting area >= 6*n and dimension-growth constraints. | Formal target enforces only validity/shape constraints and omits minimality optimization over feasible dimensions. | Always output a deliberately oversized valid rectangle. | fully_executable | True | False | True |
| DA0208 |  | optimization_missing | Return the minimum feasible common box size so all cowbells fit in at most k boxes with capacity constraints. | Formal target for solve only ensures result >= 0 and does not encode feasibility/minimization semantics. | Always return 0. | fully_executable | True | False | True |
| DA0244 |  | optimization_missing | Return the minimum possible total number of marks below water level across all days. | Method postcondition enforces only result >= 0 and omits the minimization relation. | Always return 0. | fully_executable | True | False | True |
| DA0293 |  | optimization_missing | Find the maximum consecutive ones achievable with at most K contiguous-range bit flips. | Method postcondition enforces only 0 <= result <= N and omits optimization/flip semantics. | Always return 0. | fully_executable | True | False | True |
| DA0306 |  | output_format_missing | Decrypt Right-Left cipher text back to the original plaintext. | Method postcondition enforces only \|result\| == \|t\| and omits any content/semantic relation to ciphertext. | Return a same-length constant string. | fully_executable | True | False | True |


## Limitations

- Manual validation.
- Not a prevalence estimate.
- Not a benchmark bug claim.
