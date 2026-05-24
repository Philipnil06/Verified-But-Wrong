# Spec Target Validity

Vericoding pipelines usually evaluate implementation validity with respect to a supplied specification. That assumes the supplied specification is itself a valid implementation-selection target.

We separate:

1. Implementation validity
   - Question: does the code satisfy the supplied public spec?
   - Artifact: public spec
   - Failure outcome: public-spec failure

2. Target validity
   - Question: does the supplied public spec preserve known intent-critical requirements?
   - Artifact: policy pack / requirement inventory
   - Failure outcome: intent gap / verified-but-wrong risk

3. Intended-behavior evaluation
   - Question: does the selected code satisfy the stronger intended behavior?
   - Artifact: hidden executable oracle
   - Failure outcome: verified-but-wrong

Verified-but-wrong is a failure of target validity:
- implementation validity passes
- target validity fails
- intended behavior fails

The Policy Audit Gate is a simple target-validity check:
- not full spec elicitation
- not unknown-unknown discovery
- checks known policy inventories before implementation selection
