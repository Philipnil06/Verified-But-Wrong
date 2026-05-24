# External Cases by Evidence Tier

| Case | Gap class | Evidence tier | Original target accepts bad candidate | Intended examples fail | Repaired target rejects bad candidate | Notes |
|---|---|---|---|---|---|---|
| DA0003 | trivial_postcondition | tier1_direct_dafny | yes | yes | yes | Clear external target-validity gap: NL requires maximizing chocolates with divisibility/tie semantics, while the formal method postcondition only requires a non-negative integer. |
| DA0208 | trivial_postcondition | tier1_direct_dafny | yes | yes | yes | Clear external target-validity gap: NL requires minimizing uniform box size under packing constraints, while formal target only ensures non-negative output. |
| DA0157 | missing_minimality | tier2_adapted_demo | no | yes | no | Clear external target-validity gap: NL requires minimum-area construction, while formal target only checks a valid enlarged rectangle. |
| DA0010 | trivial_postcondition | tier2_adapted_demo | no | yes | no | Clear external target-validity gap: NL requires simulation of overflow dynamics, but formal target mainly constrains range and a few edge cases. |
| DA0244 | trivial_postcondition | tier2_adapted_demo | no | yes | no | Clear external target-validity gap: NL requires minimizing a cross-day objective, while the formal target only enforces non-negative output. |
| DA0293 | trivial_postcondition | tier2_adapted_demo | no | yes | no | Clear external target-validity gap: NL requires optimization over flip operations, while the formal target constrains only result range. |
| DA0306 | missing_tiebreak | tier2_adapted_demo | no | yes | no | Clear external target-validity gap: NL requires decryption semantics, while the formal target only constrains output length. |
