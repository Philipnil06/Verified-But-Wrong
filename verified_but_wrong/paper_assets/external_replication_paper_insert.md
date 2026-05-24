# External Replication Suite (Paper Insert Draft)

## Methods Insert
We extend the external audit into a scanner-ranked external replication suite. We inspect all 41 high-confidence scanner candidates under a frozen labeling protocol. This is not prevalence evidence: the suite is scanner-ranked and enriched for likely gaps. Its purpose is to test whether the verified-but-wrong mechanism can be reproduced on externally sourced benchmark tasks, and whether repaired targets block the same bad candidates.

Each case is labeled as Tier 1 direct-Dafny VBW, Tier 1 direct-Dafny VBW plus repaired-target rejection, Tier 2 adapted executable demonstration, reject categories, or deferred. Tier 1 uses direct-Dafny verification against reconstructed original benchmark targets (`vc-preamble` + `vc-spec`) and independent intended-example failure checks. Repaired-target checks test whether the same bad candidate is blocked after adding missing target-validity conditions.

## Results Insert
The replication outputs provide: (i) complete high-confidence inventory, (ii) per-case adjudication JSONL, (iii) direct-Dafny summaries, (iv) repaired-target summaries, and (v) intended-example summaries. Summary counts and case-level evidence are reported in:
- `external_replication_summary_table.md`
- `external_replication_cases_table.md`
- `external_replication_repair_table.md`

For K Tier 1 cases, the same bad candidate verifies against the reconstructed original target but fails after adding the missing target-validity condition. This is a local mechanism check and not a full repaired benchmark specification.

## Discussion Insert
This strengthens claim boundaries by separating demonstration evidence from population claims. The scanner-ranked external replication suite supports mechanism replication on externally sourced tasks, but remains not prevalence evidence. If non-trivial-postcondition direct-Dafny replication succeeds, that broadens Tier 1 class coverage. If not, Tier 1 remains limited to currently successful classes and Tier 2 remains supportive evidence.
