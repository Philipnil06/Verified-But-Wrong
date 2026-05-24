# Known vs Unknown Policy Report

Our gate is designed for known-but-omitted requirements, not unknown unknowns.

- with loyalty policy pack: `REVIEW`, missing=[]
- without loyalty policy pack: `ALLOW`, missing=['generic.invalid_inputs_fail']

If no policy, human, or system has written the requirement down, the audit gate cannot reliably catch it.