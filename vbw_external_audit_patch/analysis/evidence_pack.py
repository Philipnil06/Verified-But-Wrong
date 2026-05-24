#!/usr/bin/env python3
"""Evidence pack helper including the external vericoding audit section.

If your repository already has analysis/evidence_pack.py, merge the constants and
external_vericoding_section() into it rather than replacing the whole file.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
EVIDENCE_PACK = REPORTS / "evidence_pack.md"

EXTERNAL_VERICODING_REPORTS = [
    REPORTS / "external_vericoding_fetch.md",
    REPORTS / "external_vericoding_inspection.md",
    REPORTS / "external_vericoding_gap_candidates.md",
    REPORTS / "external_vericoding_manual_pack.md",
    REPORTS / "external_vericoding_validated_cases.md",
    REPORTS / "external_vericoding_known_issue_context.md",
    REPORTS / "paper_insert_external_vericoding_audit.md",
]


def read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def external_vericoding_summary_table() -> str:
    fetch = read_json(REPORTS / "external_vericoding_fetch.json")
    inspection = read_json(REPORTS / "external_vericoding_inspection.json")
    scan = read_json(REPORTS / "external_vericoding_gap_candidates.json")
    validated = read_json(REPORTS / "external_vericoding_validated_cases.json")
    dataset = fetch.get("dataset") or inspection.get("dataset") or {}
    rows = [
        ("Data status", fetch.get("status", "unknown")),
        ("Repo/source", dataset.get("repo_name", "unknown")),
        ("Commit/hash", dataset.get("commit_hash", "unknown")),
        ("Tasks inspected", inspection.get("total_records", "unknown")),
        ("Useful NL descriptions", inspection.get("total_with_useful_description", "unknown")),
        ("Candidate gaps", scan.get("candidate_count", "unknown")),
        ("Validated cases", validated.get("validated_case_count", 0)),
        ("VBW demos", validated.get("verified_but_wrong_demo_count", 0)),
        ("Paper-ready", validated.get("paper_ready", False)),
    ]
    out = ["| Field | Value |", "| --- | --- |"]
    for k, v in rows:
        out.append(f"| {k} | `{v}` |")
    return "\n".join(out) + "\n"


def external_vericoding_section() -> str:
    lines = ["# External Vericoding Benchmark Audit", "", external_vericoding_summary_table(), ""]
    any_report = False
    for path in EXTERNAL_VERICODING_REPORTS:
        if path.exists():
            any_report = True
            lines += [f"## {path.name}", "", path.read_text(encoding="utf-8"), ""]
    if not any_report:
        lines += ["No external vericoding audit reports were found. Run `python run_all_repro.py` first.", ""]
    return "\n".join(lines)


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    existing = EVIDENCE_PACK.read_text(encoding="utf-8") if EVIDENCE_PACK.exists() else ""
    section = external_vericoding_section()
    marker = "# External Vericoding Benchmark Audit"
    if marker in existing:
        before = existing.split(marker, 1)[0].rstrip()
        content = (before + "\n\n" + section).strip() + "\n"
    else:
        content = (existing.rstrip() + "\n\n" + section).strip() + "\n" if existing else section
    EVIDENCE_PACK.write_text(content, encoding="utf-8")
    print(f"Wrote {EVIDENCE_PACK}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
