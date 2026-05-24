#!/usr/bin/env python3
"""Best-effort reproduction runner with optional external vericoding audit.

This file is safe as a reference implementation. In an existing repository,
merge the external audit block into the existing runner rather than replacing
project-specific internal commands.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "reports"


def run(cmd: List[str], required: bool = False) -> int:
    print("\n$ " + " ".join(cmd), flush=True)
    p = subprocess.run(cmd, cwd=ROOT, text=True)
    if p.returncode != 0:
        msg = f"Command failed with exit code {p.returncode}: {' '.join(cmd)}"
        if required:
            raise SystemExit(msg)
        print("WARN/SOFT-FAIL: " + msg)
    return p.returncode


def run_if_exists(cmd: List[str], required: bool = False) -> int:
    target = ROOT / cmd[1] if len(cmd) > 1 else None
    if target and not target.exists():
        print(f"SKIP: {cmd[1]} not found")
        return 0
    return run(cmd, required=required)


def json_report(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def external_data_available() -> bool:
    candidates = [
        ROOT / "external_data" / "vericoding-benchmark" / "jsonl" / "dafny_tasks.jsonl",
        ROOT / "external_data" / "vericoding" / "benchmarks" / "dafny_tasks.jsonl",
    ]
    return any(p.exists() for p in candidates)


def write_external_summary() -> None:
    fetch = json_report(REPORTS / "external_vericoding_fetch.json") or {}
    inspect = json_report(REPORTS / "external_vericoding_inspection.json") or {}
    scan = json_report(REPORTS / "external_vericoding_gap_candidates.json") or {}
    validated = json_report(REPORTS / "external_vericoding_validated_cases.json") or {}
    rows = [
        "# External Vericoding Audit Reproduction Summary",
        "",
        f"- Data status: `{fetch.get('status', 'unknown')}`",
        f"- Dataset source: `{(fetch.get('dataset') or inspect.get('dataset') or {}).get('repo_name', 'unknown')}`",
        f"- Commit/hash: `{(fetch.get('dataset') or inspect.get('dataset') or {}).get('commit_hash', 'unknown')}`",
        f"- Tasks inspected: `{inspect.get('total_records', inspect.get('records_total', 'unknown'))}`",
        f"- Useful NL descriptions: `{inspect.get('total_with_useful_description', 'unknown')}`",
        f"- Candidate gaps: `{scan.get('candidate_count', 'unknown')}`",
        f"- Validated cases: `{validated.get('validated_case_count', 0)}`",
        f"- VBW demos: `{validated.get('verified_but_wrong_demo_count', 0)}`",
        f"- Paper-ready: `{validated.get('paper_ready', False)}`",
        "",
    ]
    (REPORTS / "external_vericoding_repro_summary.md").write_text("\n".join(rows), encoding="utf-8")


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)

    # Preserve likely existing internal reproduction steps by only running them if
    # present. Real repos should keep their existing command list and add the
    # external block below.
    existing_commands = [
        [sys.executable, "run_internal_benchmark.py"],
        [sys.executable, "analysis/candidate_set_analysis.py"],
        [sys.executable, "analysis/noisy_policy_pack_eval.py"],
        [sys.executable, "external_adapted_issue_suite/run_suite.py"],
        [sys.executable, "formal_demo/run_formal_demo.py"],
        [sys.executable, "analysis/llm_smoke_pilot.py"],
    ]
    for cmd in existing_commands:
        run_if_exists(cmd, required=False)

    # External vericoding audit. Soft-fails when network/data are unavailable.
    run([sys.executable, "external_vericoding_audit/fetch_external_benchmark.py", "--repo", "auto"], required=False)
    if external_data_available():
        run([sys.executable, "external_vericoding_audit/inspect_dafny_jsonl.py"], required=False)
        run([sys.executable, "external_vericoding_audit/scan_target_validity_gaps.py"], required=False)
        if (REPORTS / "external_vericoding_gap_candidates.json").exists():
            run([sys.executable, "external_vericoding_audit/make_manual_validation_pack.py", "--top", "10"], required=False)
        run([sys.executable, "external_vericoding_audit/validate_external_cases.py"], required=False)
    else:
        print("External vericoding audit skipped: no supported JSONL path available after fetch.")
    run([sys.executable, "external_vericoding_audit/write_known_issue_context.py"], required=False)
    write_external_summary()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
