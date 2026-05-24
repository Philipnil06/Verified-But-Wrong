#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "external_vericoding_cases"
OUT = ROOT / "results" / "external_replication"

VALIDATED = {"DA0003", "DA0010", "DA0157", "DA0208", "DA0244", "DA0293", "DA0306"}
KNOWN_REJECT = {"DA0136", "DA0045", "DA0199", "DA0258", "DA0265"}

LABEL_MAP = {
    "tier1_direct_dafny": "tier1_direct_dafny",
    "tier1_direct_dafny_repaired_blocks": "tier1_direct_dafny_repaired_blocks",
    "tier2_adapted_demo": "tier2_adapted_demo",
    "reject_spec_stronger": "reject_spec_stronger",
    "reject_nl_ambiguous": "reject_nl_ambiguous",
    "reject_bad_candidate_not_defensible": "reject_bad_candidate_not_defensible",
    "deferred": "deferred",
}


def load_jsonl(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def infer_gap_class(cat: str) -> str:
    mapping = {
        "trivial_postcondition": "trivial_postcondition",
        "optimization_missing": "missing_minimality",
        "conservation_or_permutation_missing": "missing_simulation_semantics",
        "exact_value_missing": "missing_exact_value",
        "tie_break_missing": "missing_tiebreak",
        "output_format_missing": "output_format",
    }
    return mapping.get(cat, "other")


def main() -> int:
    inv = load_jsonl(OUT / "high_confidence_inventory.jsonl")
    rows = []
    remaining = []
    for r in inv:
        case_id = r["case_id"]
        case_dir = CASES / f"candidate_{case_id}"
        manual_path = case_dir / "manual_validation.json"
        manual = {}
        if manual_path.exists():
            manual = json.loads(manual_path.read_text(encoding="utf-8"))

        if case_id in {"DA0003", "DA0208"}:
            label = "tier1_direct_dafny"
            claim = "strongest"
            direct = "pass"
        elif case_id in VALIDATED:
            label = "tier2_adapted_demo"
            claim = "supportive"
            direct = "not_attempted"
        elif case_id in KNOWN_REJECT:
            label = "reject_bad_candidate_not_defensible"
            claim = "not_counted"
            direct = "not_attempted"
        else:
            label = "deferred"
            claim = "not_counted"
            direct = "not_attempted"

        row = {
            "case_id": case_id,
            "label": label,
            "gap_class": infer_gap_class(str(r.get("scanner_gap_category", ""))),
            "nl_intent_summary": str(manual.get("nl_requirement", ""))[:300],
            "formal_target_gap_summary": str(manual.get("formal_spec_gap", ""))[:300],
            "bad_candidate_summary": str(manual.get("bad_candidate_behavior", ""))[:300],
            "direct_dafny_status": direct,
            "direct_dafny_log_path": "",
            "intended_examples_status": "fail" if label.startswith("tier") else "not_available",
            "intended_examples": [],
            "repaired_target_status": "not_attempted",
            "repaired_target_log_path": "",
            "manual_notes": str(manual.get("reviewer_notes", ""))[:400],
            "why_counted_or_rejected": str(manual.get("reason", "autofill; manual adjudication required for deferred/reject cases")),
            "claim_strength": claim,
        }
        rows.append(row)
        if label == "deferred":
            remaining.append({"case_id": case_id, "scanner_gap_category": r.get("scanner_gap_category"), "scanner_reason": r.get("scanner_reason")})

    with (OUT / "adjudication.jsonl").open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    with (OUT / "adjudication_template_remaining.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["case_id", "scanner_gap_category", "scanner_reason"])
        w.writeheader()
        w.writerows(remaining)

    print(f"wrote adjudication rows: {len(rows)}; deferred: {len(remaining)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
