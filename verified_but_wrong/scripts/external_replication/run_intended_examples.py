#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "external_vericoding_cases"
OUT = ROOT / "results" / "external_replication"


def run_case(case_id: str):
    p = CASES / f"candidate_{case_id}" / "intended_examples.json"
    if not p.exists():
        return None
    data = json.loads(p.read_text(encoding="utf-8"))
    rows = data.get("examples", [])
    fail = any(not e.get("pass", False) for e in rows)
    return {
        "case_id": case_id,
        "expected_outputs": [e.get("expected") for e in rows],
        "bad_candidate_outputs": [e.get("bad_candidate") for e in rows],
        "pass_or_fail": "fail" if fail else "pass",
        "notes": "Dafny verifies formal target separately; intended behavior checked via independent examples.",
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    case_ids = sorted([p.name.replace("candidate_", "") for p in CASES.glob("candidate_*")])
    results = [r for cid in case_ids if (r := run_case(cid)) is not None]

    with (OUT / "intended_examples_summary.jsonl").open("w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    with (OUT / "intended_examples_summary.csv").open("w", newline="", encoding="utf-8") as f:
        if results:
            w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
            w.writeheader()
            w.writerows(results)

    md = ["# Intended Examples Summary", "", "| Case | pass_or_fail | Notes |", "|---|---|---|"]
    for r in results:
        md.append(f"| {r['case_id']} | {r['pass_or_fail']} | {r['notes']} |")
    (OUT / "intended_examples_summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"wrote intended-example summaries: {len(results)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
