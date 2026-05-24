# Verified but Wrong: Intent-Gap Auditing for Vericoding Pipelines

Specification omission failures in spec-driven implementation selection.

## What This Is

Verified but Wrong is a deterministic benchmark and pre-selection policy audit gate for vericoding pipelines.

Core claim: vericoding shifts the trust boundary from generated code to specification coverage. If the public spec omits intent-critical requirements, the pipeline can select code that is verified against the spec but wrong against intended behavior.

## Why It Matters

Spec-driven systems should not blindly trust generated specs. The practical safety layer is:

```text
Public spec -> Policy Audit Gate -> Candidate selection -> Hidden executable oracle
```

The hidden oracle is evaluation-only. The deployable gate uses public spec text plus separate policy packs.

## Quickstart

```powershell
pip install -r requirements.txt
py -m streamlit run app.py
```

No API key is required for deterministic reproduction.

## Reproduce Results

Run all non-API experiments:

```powershell
py run_all_repro.py
```

Individual commands:

```powershell
py run_benchmark.py --suite controlled --out results/controlled_benchmark_latest.json
py run_audit_gate.py
py run_repair_experiment.py
py run_defense_baselines.py
py run_ablation.py
py run_naturalistic_experiment.py
py analyze_results.py
```

## Main Results

Current controlled benchmark:

- Naive specs: `12/12` verified-but-wrong.
- Checklist critic specs: `5/12` verified-but-wrong.
- Oracle specs: `0/12` verified-but-wrong.
- Policy gate: `0` dangerous controlled specs allowed.
- Repair loop: naive `12 -> 0`, critic `5 -> 0`.
- Naturalistic docs: `12` product-ticket-style fixtures, dangerous docs allowed `0`, verified-but-wrong after repair `0`.
- Candidate-set underconstraint analysis: naive specs admit hidden-failing public-spec-passing candidates across the suite; oracle and policy-targeted repaired specs drive aggregate underconstraint risk to `0.00`.
- Noisy policy-pack robustness: the gate remains useful under noisy packs, while incomplete packs honestly lose recall when the causally relevant policy is removed.
- External adapted issue suite: includes the Kibana-derived sanity-check case plus additional adapted public issue patterns.
- Formal demo: includes a tiny illustrative contract demo with graceful skip if Dafny is unavailable.

These are controlled benchmark results, not real-world prevalence estimates.

## Policy Packs Explained

The audit gate does not know the hidden oracle. It checks public specs against separate policy packs / critical requirement inventories.

Policy packs live in `policy_packs/` and contain policy cards:

- requirement text
- category
- severity
- applies-to task list
- keywords
- why it matters
- suggested spec patch
- audit question
- optional requirement-test mapping

This models how an organization might maintain compliance rules, security policies, domain invariants, and business constraints outside a single implementation spec.

## Evaluation Split

The split is documented in `EVALUATION_FREEZE.md` and `evaluation_manifest.json`.

- Development executable tasks: `8`
- Heldout executable tasks: `4`
- Naturalistic product-ticket-style docs: `12`
- External docs: none currently

Heldout tasks are author-created executable fixtures used after the policy gate framing was fixed. They are not externally sourced and should not be described as real production tasks.

## Spec Audit Gate Explained

The gate has two decisions:

- `pre_selection_decision`: deployable decision based only on public spec and policy packs.
- `post_selection_decision`: evaluation-only decision that may include downstream verified-but-wrong status.

Decision levels:

- `ALLOW`: no critical policy gap detected.
- `REVIEW`: unclear/high-risk policy coverage needs human review or spec repair.
- `BLOCK`: load-bearing policy requirement is missing.

## Repair Loop

`spec_repair.py` appends deterministic suggested patches from missing/unclear policy cards, re-audits the repaired spec, maps covered policy cards to curated requirement tests, and re-runs selection.

Generated patch text is never executed as code.

Repair baselines are reported in `results/spec_repair_baselines_report.md`:

- no repair
- generic repair
- checklist repair
- policy-targeted repair
- oracle repair upper bound

## Defense Baselines

`defense_baselines.py` compares:

- No audit
- Generic checklist audit
- Checklist critic only
- Policy Audit Gate
- Hidden oracle post-selection

This answers whether the policy gate improves over trivial or non-deployable defenses.

Threshold profiles are reported in `results/policy_gate_threshold_sweep.md`. The default profile is selected because it preserves zero dangerous escapes in the current controlled/heldout suite while allowing most safe specs.

## Naturalistic Specs

`naturalistic_specs/` contains longer product-ticket style docs with:

- public ticket
- policy pack reference
- oracle notes for evaluation

`naturalistic_experiment.py` audits these docs, runs selection where possible, repairs specs, and evaluates hidden oracle outcomes.

## Candidate-Set Underconstraint

`analysis/candidate_set_underconstraint.py` checks the whole candidate set for each task/spec mode:

- how many candidates pass the public spec
- how many of those still fail the hidden oracle
- whether existence risk remains even if the selected candidate changes

This supports a stronger claim than fixed-order selection alone: incomplete specs underconstrain the implementation target.

## Noisy Policy-Pack Robustness

`analysis/noisy_policy_pack_eval.py` perturbs policy inventories with:

- irrelevant-card noise
- incomplete policy coverage
- outdated wording

The report makes the tradeoff explicit: dangerous-spec recall, safe-spec allow rate, causal-policy identification, and review burden.

## External Adapted Issue Suite

`analysis/external_issue_suite_eval.py` evaluates an externally sourced adapted issue suite. These cases use public GitHub issue patterns adapted into minimal vericoding-style cases. They are sanity checks, not bug reproductions.

## External Vericoding Benchmark Audit

Optional soft-failing external audit pipeline:

```powershell
py -3 external_vericoding_audit/fetch_external_benchmark.py --repo auto
py -3 external_vericoding_audit/inspect_dafny_jsonl.py
py -3 external_vericoding_audit/scan_target_validity_gaps.py
py -3 external_vericoding_audit/make_manual_validation_pack.py --top 20
py -3 external_vericoding_audit/validate_external_cases.py
py -3 external_vericoding_audit/write_known_issue_context.py
```

This layer audits paired NL intent and Dafny formal targets from public external data for candidate target-validity gaps. Candidate scans are not validated evidence until manually reviewed.

## Tiny Formal Demo

`formal_demo/` contains a small illustrative contract demo. If `dafny` is installed, reproduction runs it. If not, reproduction writes a skipped result and continues.

## Live LLM Pilot

Optional live LLM spec generation is supported through `.env`:

```powershell
Copy-Item .env.example .env
```

Then set:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_SPEC_MODEL=gpt-5.4-nano
```

Do not commit `.env`.

Saved LLM artifacts are reproducible without API calls. Optional naturalistic LLM support requires an explicit `--run-api true` flag and is not run by default.

`run_llm_policy_split.py` adds a cache-first policy-split experiment with these conditions:

- `ticket_only`
- `ticket_plus_generic_checklist`
- `ticket_plus_retrieved_policy`
- `oracle_full`

Normal reproduction does not make API calls. If cached responses exist, they are reused. Live refresh requires an explicit `--refresh`.

## Limitations

- Small controlled benchmark.
- Policy packs are manually curated.
- Keyword coverage is auditable but not semantic proof.
- Requirement-to-test mapping is manual.
- Hidden oracles approximate intended behavior.
- Live LLM pilot is not a prevalence estimate.
- No Lean/Dafny/Z3 integration yet.

## How To Add A New Task

1. Add `tasks/<task_id>/task.json`.
2. Add `specs/public_spec_naive.py`, `public_spec_critic.py`, optional `public_spec_oracle.py`, and `hidden_oracle.py`.
3. Add candidates.
4. Add `requirement_tests/requirement_tests.py`.
5. Add policy cards in `policy_packs/`.
6. Add task-to-pack mapping in `policy_pack.py`.

## How To Add A Policy Card

Add a JSON object with:

- `id`
- `title`
- `requirement`
- `category`
- `severity`
- `applies_to_tasks`
- `keywords`
- `why_it_matters`
- `suggested_spec_patch`
- `audit_question`
- optional `requirement_test`

## CI/CD Demo

```powershell
py ci_demo/run_ci_audit.py
```

The demo blocks a spec that omits loyalty reversal while the policy pack requires it.

## Artifact Index

- `results/final_submission_paper.md`
- `results/final_submission_abstract.md`
- `results/final_submission_60_second_pitch.md`
- `results/final_submission_demo_script.md`
- `results/final_submission_judge_rebuttals.md`
- `results/final_submission_tables.md`
- `results/final_submission_checklist.md`
- `results/final_submission_one_page_summary.md`
- `results/policy_gate_calibration_report.md`
- `results/policy_gate_threshold_sweep.md`
- `results/spec_repair_report.md`
- `results/spec_repair_baselines_report.md`
- `results/defense_baselines_report.md`
- `results/audit_gate_ablation_report.md`
- `reports/candidate_set_underconstraint.md`
- `reports/noisy_policy_pack_eval.md`
- `reports/external_issue_suite_eval.md`
- `reports/formal_demo_result.md`
- `reports/llm_policy_split_eval.md`
- `reports/evidence_pack.md`
- `results/naturalistic_experiment_report.md`
- `results/provenance_table.md`
- `results/policy_pack_index.md`
- `results/known_vs_unknown_policy_report.md`
- `results/stats_summary.md`
- `results/reproduction_log_latest.md`
## External VBW Replication Suite

This scanner-ranked external replication suite tests whether verified-but-wrong mechanisms reproduce on externally sourced vericoding tasks. It is demonstration evidence, not prevalence evidence.

### What It Tests
- scanner-ranked external replication suite over all 41 high-confidence candidates from the 128 scanner candidates
- direct-Dafny verification against reconstructed original benchmark targets for Tier 1 cases
- repaired-target check for whether the same bad candidate is blocked
- adapted executable demonstrations for supportive Tier 2 cases

### What It Does Not Test
- it is not a population estimate
- deferred or non-inspected cases are not findings
- repaired-target checks are local mechanism checks, not full benchmark-wide fixes

### Reproduce
- `dotnet tool restore`
- `py -3 run_external_replication.py`
- `py -3 run_external_replication.py --skip-random-control`

### Outputs
- `results/external_replication/*`
- `paper_assets/external_replication_summary_table.md`
- `paper_assets/external_replication_cases_table.md`
- `paper_assets/external_replication_repair_table.md`
- `paper_assets/evidence_stack_figure_data.json`

### Evidence Tiers
- `tier1_direct_dafny`: direct verifier pass against reconstructed original target + intended-example failure
- `tier1_direct_dafny_repaired_blocks`: Tier 1 plus repaired target rejects same bad candidate
- `tier2_adapted_demo`: adapted demonstration evidence without direct original-target Dafny verification

### Claim Boundaries
- not prevalence evidence
- not all candidates are findings unless adjudicated and non-deferred
- Tier 1 and Tier 2 provide different evidence strength
- repaired-target checks are local mechanism checks

### Paper Citation Guidance
Use language: scanner-ranked external replication suite; demonstration evidence; not prevalence evidence; direct-Dafny verification against reconstructed original benchmark targets; repaired-target check; known external benchmark artifacts.
