# Formal Demo Result

This is a tiny illustrative Dafny demo, not an integration of the full benchmark with a proof assistant.

- status: `skipped_dafny_not_installed`
- dafny found: `False`
- dafny version: `unknown`

| Check | Contract | Expected | Result |
|---|---|---|---|
| No checks run | - | - | - |

## Interpretation

Dafny was not found on PATH, so the illustrative contract demo was not executed.

## Limitations

- This machine does not currently have Dafny installed or discoverable on PATH.
- The reproduction script treats this as a soft skip.

## Run Instructions

- Install Dafny and ensure `dafny` is on `PATH`.
- Run `python formal_demo/run_formal_demo.py`.
- Or verify the files directly with `dafny verify formal_demo/impl_verified_against_public.dfy`, `dafny verify formal_demo/impl_fails_intended_contract.dfy`, and `dafny verify formal_demo/repaired_impl.dfy`.