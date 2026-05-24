# Kibana Role Downgrade Session Invalidation Case Study

## Framing

This is an externally sourced public software-requirements artifact adapted into a minimal vericoding-style case study.

We do not claim to reproduce the original Kibana bug. We adapt the public issue into a deterministic case study about stale privileged access after role downgrade.

## Source

- Repository: `elastic/kibana`
- Issue: `#192346`
- URL: https://github.com/elastic/kibana/issues/192346

## Result

- before repair selected candidate: `impl_1_update_role_only.py`
- before repair public spec passed: `True`
- before repair hidden oracle passed: `False`
- before repair verified-but-wrong: `True`
- gate decision: `BLOCK`
- missing policy: `auth.role_downgrade.session_invalidation`
- category: `authorization_omission`
- severity: `high`
- after repair selected candidate: `impl_3_revalidate_permissions.py`
- after repair hidden oracle passed: `True`
- after repair verified-but-wrong: `False`

## External Case Table

| Case | Source | Omitted policy | Gate | Before repair | After repair |
|---|---|---|---|---|---|
| Role downgrade session invalidation | Public GitHub issue | Active sessions after privilege downgrade | BLOCK | VBW | pass |

## Gate Access Boundary

The deployable audit gate sees only the extracted public spec and policy pack. It does not see the hidden oracle, selected candidate, or verified-but-wrong status.

## Suggested Repair

When a user's role is downgraded or privileged access is removed, existing sessions must not continue to authorize privileged actions; invalidate active sessions or revalidate permissions server-side before every privileged action.