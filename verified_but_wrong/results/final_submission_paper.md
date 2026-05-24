# Verified but Wrong: Intent-Gap Auditing for Vericoding Pipelines

## Abstract

Spec-driven development and vericoding pipelines aim to make generated code safer by selecting implementations that satisfy written specifications. This shifts a central trust problem from code to the specification: if the public spec omits an intent-critical requirement, a pipeline may select code that is verified against the spec but wrong against intended behavior.

We introduce Verified-but-Wrong, an evaluation outcome for specification omission failures in vericoding pipelines. Our harness selects candidate implementations against a public spec, then evaluates the selected implementation against a hidden executable oracle representing intended behavior. We separate public specs from policy packs and hidden oracles: the deployable gate sees only public spec text and policy cards, while hidden oracles are evaluation-only.

In the current 12-task executable suite, naive specs produce 12/12 verified-but-wrong selections, checklist critic specs produce 5/12, and oracle specs produce 0/12. The policy audit gate catches 17/17 dangerous specs and allows 0. Safe allow rate is 0.7895. Policy-targeted repair reduces naive failures from 12 to 0 and critic failures from 5 to 0. Naturalistic product-ticket-style fixtures show 8 verified-but-wrong selections before repair and 0 after repair.

## Introduction

A refund implementation can pass every public test and still be wrong. If the public spec says to refund the customer but omits the organization's rule that loyalty points from the original purchase must be reversed proportionally, a spec-driven pipeline can select an implementation that is verified against the spec and wrong against intended behavior.

This is not primarily a code-generation failure. It is a verification-target failure.

## Failure Model

VBW = Pass(public_spec, selected_impl) AND Fail(hidden_oracle, selected_impl).

- Public spec: used for implementation selection.
- Policy pack / requirement inventory: organization-maintained rules available to the audit gate.
- Hidden executable oracle: evaluation-only behavior checks.
- Known omitted policy: written in a policy pack but absent from the public spec.
- Unknown missing intent: not present in any policy inventory; the gate cannot solve this.

## Harness

Public Spec -> Policy Audit Gate -> Candidate Selection -> Hidden Executable Oracle.

The audit gate does not discover unknown intent. It checks whether a public implementation spec preserves requirements from an independently maintained policy inventory.

## Key Tables

| mode | tasks | verified-but-wrong |
|---|---:|---:|
| naive | 12 | 12 |
| critic | 12 | 5 |
| oracle | 12 | 0 |

| gate metric | value |
|---|---:|
| dangerous caught | 17 |
| dangerous allowed | 0 |
| safe allow rate | 0.7895 |
| safe block rate | 0.2105 |

| repair mode | before | after |
|---|---:|---:|
| naive | 12 | 0 |
| critic | 5 | 0 |

## What This Does Not Claim

- We do not claim current LLMs always omit critical requirements.
- We do not claim real-world prevalence.
- We do not solve unknown requirement discovery.
- We do not claim the gate guarantees correctness.
- We do not use the hidden oracle in deployable pre-selection audit.
- We do not model hazardous bio protocols.

## Safety-Critical Relevance

This work is software/system-safety oriented: access control, audit logs, redaction, chain-of-custody, approvals, sample tracking, lab inventory, and compliance workflows. We do not model hazardous biological protocols. We model the software failure class: safety-relevant requirements omitted from implementation specs before automated code selection.


## Externally Sourced Case Study

We adapted a public Kibana RBAC issue into a minimal vericoding-style case study. We do not claim to reproduce the original bug. The extracted public spec captures role update behavior but omits the policy requirement that privilege-reducing role changes must invalidate or revalidate active sessions.

The same verified-but-wrong pattern appears: before repair the selected candidate is `impl_1_update_role_only.py`, the public spec passes, and the hidden oracle fails. The policy gate returns `BLOCK` before implementation selection. Targeted repair adds the missing session-invalidation/revalidation policy and removes the failure.

| Case | Source | Omitted policy | Gate | Before repair | After repair |
|---|---|---|---|---|---|
| Role downgrade session invalidation | Public GitHub issue | Active sessions after privilege downgrade | BLOCK | VBW | pass |

We additionally include an externally sourced adapted issue suite of 4 public issue-pattern cases in the reproduction artifacts. These remain sanity checks, not bug reproductions or prevalence claims.


## Limitations

The benchmark is controlled and partly author-created. Policy packs must exist. Coverage is rule-based. Hidden oracles approximate intended behavior. The audit gate is a risk filter, not proof of correctness.

## Conclusion

Verified is not correct when the specification is incomplete.
