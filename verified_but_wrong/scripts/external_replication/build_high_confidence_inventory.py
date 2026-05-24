#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports"
CASES = ROOT / "external_vericoding_cases"
JSONL = ROOT / "external_data" / "vericoding-benchmark" / "jsonl" / "dafny_tasks.jsonl"
OUT = ROOT / "results" / "external_replication"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    scan = load_json(REPORTS / "external_vericoding_gap_candidates.json")
    tasks = {str(r.get("id")): r for r in load_jsonl(JSONL)}

    candidates = scan.get("candidates", [])
    high = [c for c in candidates if str(c.get("confidence", "")).lower() == "high"]
    high_sorted = sorted(high, key=lambda c: (-int(c.get("score", 0)), str(c.get("id", "")), str(c.get("gap_category", ""))))

    rows = []
    for idx, c in enumerate(high_sorted, start=1):
        case_id = str(c.get("id"))
        case_dir = CASES / f"candidate_{case_id}"
        rec = tasks.get(case_id, {})
        row = {
            "case_id": case_id,
            "source_dataset": rec.get("source") or c.get("source"),
            "benchmark_record_id": case_id,
            "original_index": rec.get("source-id") or c.get("source_id"),
            "vc_description": rec.get("vc-description", ""),
            "vc_preamble": rec.get("vc-preamble", ""),
            "vc_spec": rec.get("vc-spec", ""),
            "scanner_confidence": c.get("confidence"),
            "scanner_gap_category": c.get("gap_category"),
            "scanner_reason": c.get("why_spec_may_be_weak"),
            "existing_status": c.get("status"),
            "candidate_priority_rank": idx,
            "direct_dafny_exists": (case_dir / "dafny_direct" / "bad_candidate.dfy").exists(),
            "adapted_demo_exists": (case_dir / "bad_candidate.py").exists() and (case_dir / "weak_spec_proxy.py").exists(),
            "existing_case_dir": str(case_dir) if case_dir.exists() else "",
            "scanner_score": c.get("score"),
        }
        rows.append(row)

    with (OUT / "high_confidence_inventory.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    csv_fields = list(rows[0].keys()) if rows else []
    with (OUT / "high_confidence_inventory.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=csv_fields)
        w.writeheader()
        w.writerows(rows)

    summary = {
        "status": "ok",
        "source_scan_file": str(REPORTS / "external_vericoding_gap_candidates.json"),
        "source_jsonl_file": str(JSONL),
        "candidate_total": len(candidates),
        "high_confidence_count": len(rows),
        "reconstruction": "high-confidence defined as confidence == 'high' from scanner output; ranking by score desc then case id.",
        "has_expected_41": len(rows) == 41,
    }
    (OUT / "high_confidence_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (OUT / "README.md").write_text(
        "\n".join([
            "# External Replication Results",
            "",
            "- `high_confidence_inventory.jsonl`: per-case inventory for scanner-ranked external replication suite.",
            "- `high_confidence_inventory.csv`: tabular view of the same inventory.",
            "- `high_confidence_summary.json`: reconstruction details and counts.",
            "- `adjudication.jsonl`: per-case frozen-label adjudications.",
            "- `dafny_logs/`: direct-Dafny and repaired-target logs.",
        ]) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(rows)} high-confidence rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
