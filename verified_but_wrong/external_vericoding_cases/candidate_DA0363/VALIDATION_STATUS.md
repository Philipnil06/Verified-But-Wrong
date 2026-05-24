# Validation Status: DA0363

Status: **candidate_needs_manual_oracle**

This case is candidate-only and not validated.

A human must check:

1. The NL/source intent genuinely requires the suspected missing behavior.
2. The Dafny `vc-spec`/`vc-preamble` does not encode that behavior.
3. The bad candidate is plausibly accepted by the weak formal target or by a carefully documented weak-spec proxy.
4. The intended oracle is task-specific and rejects the bad candidate on selected inputs.

A valid VBW demo requires:

- `manual_validation.json` exists.
- `manual_validation.json.status == "validated"`.
- `bad_candidate.py` exists.
- `intended_oracle.py` exists and runs task-specific tests.
- Either `weak_spec_proxy.py` passes or `manual_validation.json` explicitly documents a non-executable proxy and sets `weak_spec_proxy_pass: true`.

Do not cite this case as validated evidence until `validate_external_cases.py` reports `verified_but_wrong_demo: true`.
