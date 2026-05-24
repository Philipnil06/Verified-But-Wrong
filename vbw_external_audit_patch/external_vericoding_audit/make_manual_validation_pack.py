#!/usr/bin/env python3
"""Create manual validation packs for top external scanner candidates.

The generated packs are deliberately conservative. They do not create fake
oracles for unknown APPS problems. Executable files are only generated when they
are narrow weak-spec proxies or clearly marked as non-validation scaffolding.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List

from common import CASES, REPORTS, fenced_excerpt, safe_case_id, write_json, write_text


def load_candidates(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("candidates", []))


def weak_proxy_template_possible(c: Dict[str, Any]) -> bool:
    spec = (c.get("spec_excerpt") or "") + "\n" + json.dumps(c.get("raw_record", {}), ensure_ascii=False)
    return bool(re.search(r"result\s*>=\s*0|0\s*<=\s*result|ensures\s+true|validresult\s*\(\s*result", spec, re.I))


def create_bad_candidate(case_dir: Path, c: Dict[str, Any]) -> None:
    body = f'''"""Candidate-only bad implementation scaffold for {c.get('id')}.

This is intentionally wrong under the NL intent. It is not validation by itself.
A human must inspect the external task and write a task-specific intended_oracle.py
before this case can be marked validated.
"""


def candidate(*args, **kwargs):
    """Return a constant value likely to satisfy very weak non-negativity specs."""
    return 0
'''
    write_text(case_dir / "bad_candidate.py", body)


def create_weak_spec_proxy(case_dir: Path, c: Dict[str, Any]) -> None:
    body = f'''"""Weak-spec proxy scaffold for {c.get('id')}.

This proxy only models the suspicious trivial/range postcondition pattern
identified by the scanner. It is not a full Dafny verification reproduction.
"""


def run_tests(candidate):
    inputs = [(), (1,), (1, 2), ([1, 2, 3],)]
    rows = []
    for args in inputs:
        try:
            actual = candidate(*args)
            ok = isinstance(actual, int) and actual >= 0
        except Exception as exc:
            actual = repr(exc)
            ok = False
        rows.append({
            "input": repr(args),
            "actual": actual,
            "weak_spec_proxy_pass": ok,
            "proxy_note": "generic non-negative-result proxy; human must replace with task-specific proxy if needed",
        })
    return rows
'''
    write_text(case_dir / "weak_spec_proxy.py", body)


def write_case(case_dir: Path, c: Dict[str, Any]) -> Dict[str, Any]:
    case_dir.mkdir(parents=True, exist_ok=True)
    task_id = str(c.get("id"))
    raw = c.get("raw_record", {})
    write_json(case_dir / "source_record.json", raw)
    write_text(case_dir / "nl_intent.md", "# Natural-Language Intent Excerpt\n\n" + fenced_excerpt(c.get("nl_excerpt", ""), lang="text") + "\n")
    write_text(case_dir / "formal_spec.dfy", (c.get("spec_excerpt") or "").strip() + "\n")
    write_text(case_dir / "gap_analysis.md", render_gap_analysis(c))

    status = "candidate_needs_manual_oracle"
    generated = ["source_record.json", "nl_intent.md", "formal_spec.dfy", "gap_analysis.md", "README.md", "VALIDATION_STATUS.md", "manual_validation.template.json"]

    if weak_proxy_template_possible(c):
        create_bad_candidate(case_dir, c)
        create_weak_spec_proxy(case_dir, c)
        generated += ["bad_candidate.py", "weak_spec_proxy.py"]
        status = "candidate_auto_pack_created_needs_manual_oracle"

    write_text(case_dir / "VALIDATION_STATUS.md", render_status(c, status))
    write_json(case_dir / "manual_validation.template.json", {
        "status": "candidate",
        "reason": "Fill this manually. Change status to validated only after task-specific human review.",
        "gap_category": c.get("gap_category"),
        "nl_requirement": "",
        "formal_spec_gap": "",
        "weak_spec_proxy_description": "",
        "weak_spec_proxy_pass": None,
        "bad_candidate_behavior": c.get("possible_bad_candidate_behavior"),
        "intended_oracle_description": "",
        "reviewer_notes": "",
    })
    write_text(case_dir / "README.md", render_readme(c, status, generated))
    return {"id": task_id, "case_dir": str(case_dir), "status": status, "generated_files": generated}


def render_gap_analysis(c: Dict[str, Any]) -> str:
    return "\n".join([
        f"# Gap Analysis: {c.get('id')}",
        "",
        "Status: **candidate only, not validated**.",
        "",
        f"Source: `{c.get('source')}` / `{c.get('source_id')}`",
        f"Category: `{c.get('gap_category')}`",
        f"Confidence: `{c.get('confidence')}`",
        "",
        "## Suspected missing requirement",
        "",
        str(c.get("suspected_missing_requirement", "")),
        "",
        "## Why the formal spec may be weak",
        "",
        str(c.get("why_spec_may_be_weak", "")),
        "",
        "## Candidate bad implementation idea",
        "",
        str(c.get("possible_bad_candidate_behavior", "")),
        "",
        "## NL excerpt",
        "",
        fenced_excerpt(c.get("nl_excerpt", ""), lang="text"),
        "",
        "## Formal spec excerpt",
        "",
        fenced_excerpt(c.get("spec_excerpt", ""), lang="dafny"),
        "",
        "## Required manual work",
        "",
        "A human must inspect the full external task, write a task-specific weak-spec proxy or document the exact proxy, write an intended oracle over selected inputs, and then create manual_validation.json with status validated or rejected.",
        "",
        "Caveat: this is an adapted target-validity demonstration candidate, not a benchmark bug claim.",
    ])


def render_status(c: Dict[str, Any], status: str) -> str:
    return f"""# Validation Status: {c.get('id')}

Status: **{status}**

This case is candidate-only and not validated.

A human must check:

1. The NL/source intent genuinely requires the suspected missing behavior.
2. The Dafny `vc-spec`/`vc-preamble` does not encode that behavior.
3. The bad candidate is plausibly accepted by the weak formal target or by a carefully documented weak-spec proxy.
4. The intended oracle is task-specific and rejects the bad candidate on selected inputs.

A valid VBW demo requires:

- `manual_validation.json` exists.
- `manual_validation.json.status == "validated"`.
- `bad_candidate.py` exists.
- `intended_oracle.py` exists and runs task-specific tests.
- Either `weak_spec_proxy.py` passes or `manual_validation.json` explicitly documents a non-executable proxy and sets `weak_spec_proxy_pass: true`.

Do not cite this case as validated evidence until `validate_external_cases.py` reports `verified_but_wrong_demo: true`.
"""


def render_readme(c: Dict[str, Any], status: str, generated: List[str]) -> str:
    generated_md = "\n".join("- `" + f + "`" for f in generated)
    return f"""# External Vericoding Candidate {c.get('id')}

Status: **{status}**

Source: `{c.get('source')}`  
Source id: `{c.get('source_id')}`  
Gap category: `{c.get('gap_category')}`  
Confidence: `{c.get('confidence')}`

## NL intent excerpt

{fenced_excerpt(c.get('nl_excerpt', ''), lang='text')}

## Formal spec excerpt

{fenced_excerpt(c.get('spec_excerpt', ''), lang='dafny')}

## Suspected missing requirement

{c.get('suspected_missing_requirement')}

## Bad candidate behavior idea

{c.get('possible_bad_candidate_behavior')}

## Generated files

{generated_md}

## Caveat

This is an adapted demonstration candidate, not a benchmark bug claim, not a real-world vulnerability claim, and not a prevalence estimate.
"""


def render_report(rows: List[Dict[str, Any]]) -> str:
    lines = [
        "# External Vericoding Manual Validation Pack",
        "",
        "Generated candidate folders are candidate-only. They are not validated evidence until manually reviewed and passed by validate_external_cases.py.",
        "",
        "| Case | Status | Folder |",
        "| --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| {row['id']} | {row['status']} | `{row['case_dir']}` |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, default=REPORTS / "external_vericoding_gap_candidates.json")
    parser.add_argument("--top", type=int, default=10)
    args = parser.parse_args()

    candidates = load_candidates(args.candidates)
    rows = []
    if not candidates:
        result = {"status": "skipped", "reason": f"No candidate report found or candidate list empty at {args.candidates}", "count": 0, "cases": []}
        write_json(REPORTS / "external_vericoding_manual_pack.json", result)
        write_text(REPORTS / "external_vericoding_manual_pack.md", render_report(rows) + "\nSkipped: no candidate gaps available.\n")
        print("Manual validation pack skipped: no candidates available")
        return 0
    for c in candidates[: args.top]:
        case_id = safe_case_id(str(c.get("id")))
        case_dir = CASES / f"candidate_{case_id}"
        rows.append(write_case(case_dir, c))

    result = {"status": "manual_pack_created", "count": len(rows), "cases": rows}
    write_json(REPORTS / "external_vericoding_manual_pack.json", result)
    write_text(REPORTS / "external_vericoding_manual_pack.md", render_report(rows))
    print(f"Created {len(rows)} manual validation candidate packs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
