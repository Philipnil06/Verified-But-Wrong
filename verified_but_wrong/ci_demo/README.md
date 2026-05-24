# CI Demo

This small example shows a pre-selection spec audit that can fail a build or require review before vericoding selection.

Run missing-policy case:

```powershell
py ci_demo/ci_policy_gate.py --spec ci_demo/spec_missing_policy.md --policy ci_demo/payments_policy_pack.json
```

Run safe case:

```powershell
py ci_demo/ci_policy_gate.py --spec ci_demo/spec_safe.md --policy ci_demo/payments_policy_pack.json
```

The missing-policy case prints `BLOCK` and exits with code `1`. The safe case prints `ALLOW` and exits with code `0`.
