# External Vericoding Manual Inspection Log

- inspected total: **24**
- validated: **7**
- rejected: **9**
- deferred: **8**

| Case | Status | Reason |
|---|---|---|
| DA0136 | rejected | formal spec stronger than scanner assumed |
| DA0152 | deferred | record has incomplete executable target (vc-spec empty, vc-code axiom stub) |
| DA0157 | validated | optimization requirement missing from formal target |
| DA0003 | validated | formal target only ensures non-negativity |
| DA0010 | validated | simulation semantics missing from formal target |
| DA0045 | rejected | formal spec encodes optimality/tie behavior |
| DA0082 | deferred | task-specific oracle would require heavier queue simulation and tie handling for defensible minimal demo |
| DA0199 | rejected | formal spec already defines exact attacking-pairs count |
| DA0208 | validated | formal target only ensures non-negativity |
| DA0244 | validated | formal target omits minimization objective |
| DA0258 | rejected | formal spec already encodes global minimum window with tie condition |
| DA0265 | rejected | formal spec already encodes best-index constraints |
| DA0281 | rejected | formal spec already encodes required witness relation for result index |
| DA0293 | validated | formal target only constrains range |
| DA0306 | validated | formal target only constrains output length |
| DA0315 | deferred | full staircase/box dynamics oracle is non-trivial for minimal adapted demo |
| DA0359 | deferred | combinatorial counting oracle is heavy for minimal adapted demo |
| DA0363 | deferred | record lacks executable solve contract in extracted formal target |
| DA0406 | deferred | bad candidate not defensible against strong explicit pattern predicate |
| DA0409 | rejected | formal target already encodes exact max-distance computation |
| DA0417 | deferred | domain dynamics oracle too heavy for minimal adapted demo |
| DA0438 | deferred | shape-counting oracle too heavy for minimal adapted demo |
| DA0515 | rejected | formal target already encodes exact output mapping |
| DA0673 | rejected | formal target already encodes exact transformed output string |

