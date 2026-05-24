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
- Known omitted policy: written in a policy pack