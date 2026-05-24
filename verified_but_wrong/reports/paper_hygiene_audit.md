# Paper Hygiene Audit

## Scope checked

- Main paper source: `results/final_submission_paper.md`
- Rewrite support source: `paper_evidence_pack.md`
- Submission-facing report inserts under `reports/`
- Key final summaries under `results/`

## Broken table status

- `results/final_submission_paper.md`: no broken markdown tables detected.
- `paper_evidence_pack.md`: no broken markdown tables detected in the failure-model/artifact-separation areas.
- `reports/paper_insert_external_vericoding_audit.md`: table renders as valid markdown.

## Section numbering status

- `results/final_submission_paper.md` heading sequence is coherent:
  - Abstract
  - Introduction
  - Failure Model
  - Harness
  - Key Tables
  - What This Does Not Claim
  - Safety-Critical Relevance
  - Externally Sourced Case Study
  - Limitations
  - Conclusion

## Placeholder status

Search terms and occurrences (file:line):

- `reported in artifact`: no matches.
- `The strongest evidence comes from`: no matches.
- `Weak spec proxy`: no matches in submission-facing paper/report sources after regeneration.
- `weak spec proxy`:
  - `external_vericoding_cases/validated_cases.example.json:9` (template example; not submission text)
  - `README_external_vericoding_audit.md:39` (patched to adapted wording)

## Terminology replacements made

- Updated user-facing validated table headers:
  - `Weak spec proxy` -> `Adapted spec check`
  - `Intended oracle` -> `Intended examples`
- Updated paper insert table columns to include:
  - `Adapted spec check`
  - `Intended examples`
  - `VBW demo`
- Updated wording in `README_external_vericoding_audit.md` to use “adapted spec check”.

## PDF regeneration status

- PDF regenerated: **No**.
- Reason: no PDF build command or LaTeX/Pandoc/Quarto pipeline found in repository docs, and no PDF artifact exists in-repo.

## Manual visual checklist (for when PDF build is available)

1. Confirm all tables render with aligned headers and row separators.
2. Confirm section headings and table captions are ordered and numbered correctly.
3. Confirm no overflow/wrapping breaks in failure-model and artifact-separation tables.
4. Confirm external audit validated-case table uses “Adapted spec check” wording.
5. Confirm no placeholder text (e.g., “reported in artifact”) remains.

