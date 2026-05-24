# External Replication Protocol

This external replication suite tests whether verified-but-wrong mechanisms can be reproduced on scanner-ranked, externally sourced vericoding tasks. It is not a prevalence estimate.

## Candidate Source
- Candidate pool: 128 external scanner candidate target-validity gaps from the existing external audit.
- Replication suite focus: all 41 high-confidence scanner candidates.
- Source benchmark: Beneficial-AI-Foundation/vericoding-benchmark Dafny tasks.

## Labels
1. `tier1_direct_dafny`
2. `tier1_direct_dafny_repaired_blocks`
3. `tier2_adapted_demo`
4. `reject_spec_stronger`
5. `reject_nl_ambiguous`
6. `reject_bad_candidate_not_defensible`
7. `deferred`

## Evidence Requirements
- `tier1_direct_dafny`
  - externally sourced Dafny task
  - natural-language intent stronger than formal target
  - reconstructed original benchmark target from original `vc-preamble` + `vc-spec`
  - deliberately wrong Dafny candidate
  - Dafny verifier passes against original/reconstructed target
  - same bad candidate fails intended-behavior examples
- `tier1_direct_dafny_repaired_blocks`
  - all Tier 1 conditions
  - repaired target rejects the same bad candidate
- `tier2_adapted_demo`
  - externally sourced task
  - clear NL intent and formal target gap
  - bad candidate passes adapted weak-spec check
  - bad candidate fails intended examples
  - no direct original-target Dafny verification
- `reject_spec_stronger`
  - reviewed evidence indicates formal target is stronger than scanner assumption
- `reject_nl_ambiguous`
  - reviewed evidence indicates NL intent is too ambiguous for defensible VBW claim
- `reject_bad_candidate_not_defensible`
  - reviewed evidence indicates proposed bad candidate is not defensible
- `deferred`
  - not enough time, missing evidence, or complexity prevented defensible adjudication

## Recording Rules
- All labels must be recorded per-case in JSONL (`results/external_replication/adjudication.jsonl`).
- Non-inspected or deferred candidates are not findings.
- Scanner precision over all 128 is not estimated unless all 128 are adjudicated.
- Repaired-target checks are mechanism checks, not full fixes.
- This suite provides demonstration evidence and not prevalence evidence.
