# Verified But Wrong

**Passing the specification is not the same as satisfying the security requirement.**

Verified But Wrong is a research prototype for finding missing requirements in
specification-driven code selection. It compares a public specification with
explicit policy requirements, then uses separate executable oracles to evaluate
whether a selected implementation actually does the intended job.

## Start with a security example

A user's administrator role is removed. The implementation updates the role,
passes the public tests, but an existing session can still perform privileged
actions. The omitted requirement is session invalidation or permission
revalidation after a role downgrade.

```text
Incomplete public spec -> selected implementation passes public tests
                       -> hidden requirement check fails
Policy audit           -> identifies missing session requirement
Repaired spec          -> selects an implementation that denies stale access
```

This is a small adaptation of a public Kibana requirements issue, **not a
reproduction of the original Kibana vulnerability**. See the
[case study](external_case_studies/kibana_role_downgrade_session_invalidation/external_case_report.md).

## Requirements

| Path | Requirements |
| --- | --- |
| Security example below | Python 3.12; standard library only; no API key |
| Python harness / Streamlit UI | Python 3.12, pip, and `verified_but_wrong/requirements.txt` |
| Browser presentation | Node.js 22 or newer and npm |
| Direct Dafny/external replication | .NET 8 SDK, pinned Dafny 4.11.0, its solver, and external benchmark data |

Commands below start in the **repository root**. First installation and external
benchmark setup need internet access. The small security example runs offline.

## Run the security example

```bash
python external_case_studies/kibana_role_downgrade_session_invalidation/run_case.py
```

Expected summary:

```text
before_repair_verified_but_wrong: True
gate_result: BLOCK
after_repair_verified_but_wrong: False
```

The script regenerates the case's `results.json` and Markdown report. Selection
uses public tests; hidden checks are evaluation-only. The audit gate in this
example is a narrow keyword/policy check, not a learned detector.

## Run the research harness

Create and activate a virtual environment, then install from the repository root:

```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r verified_but_wrong/requirements.txt
cd verified_but_wrong
python runner.py
```

`runner.py` runs the small executable candidate-selection benchmark. For the
broader pipeline, from that **same subdirectory**:

```bash
python run_all_repro.py
```

This broader command regenerates reports, uses cached LLM results, attempts the
formal demo, and invokes an external benchmark audit. It is not a minimal
offline smoke test. Inspect component statuses in its generated reproduction
log: skipped or unavailable components are not successful proofs. Fresh LLM
runs are separate, opt-in commands.

## Direct Dafny and external replication

From the repository root:

```bash
dotnet tool restore
```

Follow the [pinned external-data setup](verified_but_wrong/external_data/README.md),
then run from the research subdirectory:

```bash
cd verified_but_wrong
python run_external_replication.py
```

The root `.config/dotnet-tools.json` pins Dafny 4.11.0. External replication uses
`dotnet tool run dafny`; the separate illustrative formal-demo helper looks for
a `dafny` executable on PATH. These are distinct paths. See
[reproduction commands](verified_but_wrong/REPRO_COMMANDS.md) for advanced runs.

## Browser presentation

[Open the hosted presentation](https://verified-but-wrong-demo.vercel.app/), or:

```bash
cd demo
npm ci
npm run dev
```

The presentation illustrates findings; it does not execute Python/Dafny
verification. Deployment uses `demo` as the Vite root, `npm run build`, and
`dist` as the output directory.

## Evidence and scope

The saved external-replication inventory reports **11 validated demonstrations**:
**3 direct-Dafny cases**, **8 adapted demonstrations**, and **3 repaired-target
blocks**. These counts belong to that inventory. The separate executable
research suite has its own task counts; an adapted Python case is not a
formally verified program.

- [Research overview](verified_but_wrong/README.md)
- [External replication results](verified_but_wrong/results/external_replication/README.md)
- [Evaluation freeze](verified_but_wrong/EVALUATION_FREEZE.md)
- [Evidence and provenance](verified_but_wrong/paper_evidence_pack.md)

Candidate sets, policy cards, and oracles are deliberately constructed research
fixtures. Passing them does not establish general software security. Large raw
artifacts and external binaries are not vendored; saved summaries and scripts
document their provenance.
