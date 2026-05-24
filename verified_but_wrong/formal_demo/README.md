# Formal Contract Demo

This directory contains a tiny illustrative Dafny demo for the verified-but-wrong failure mode.

What it shows:
- an incomplete implementation can verify against an incomplete public contract
- the same incomplete implementation should fail verification against the stronger intended contract
- a repaired implementation that invalidates the privileged session on downgrade should verify against the intended contract

How to run:
- `python formal_demo/run_formal_demo.py`

If Dafny is installed:
- `dafny verify formal_demo/impl_verified_against_public.dfy`
- `dafny verify formal_demo/impl_fails_intended_contract.dfy`
- `dafny verify formal_demo/repaired_impl.dfy`

If Dafny is missing:
- `run_all_repro.py` will skip the demo and write `reports/formal_demo_result.json`
- install Dafny, ensure `dafny` is on `PATH`, then rerun the command above

This is illustrative only. It is not full benchmark integration with a proof assistant.
