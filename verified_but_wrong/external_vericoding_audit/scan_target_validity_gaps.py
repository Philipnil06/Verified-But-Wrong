#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

from common import (
    REPORTS,
    fenced_excerpt,
    is_trivial_or_shape_only_spec,
    load_jsonl,
    markdown_table,
    normalize_record,
    resolve_dafny_jsonl_path,
    short_excerpt,
    spec_strength_score,
    useful_description,
    write_json,
    write_skipped_report,
    write_text,
)

CATEGORY_DEFS = {
    "optimization_missing": {
        "nl": [r"\bmaximum\b", r"\bminimum\b", r"\boptimal\b", r"\blargest\b", r"\bsmallest\b", r"\bgreatest\b", r"\bleast\b", r"\bk\s*-?th\b", r"\bbest\b", r"maximum possible"],
        "strong_spec": ["forall", "max", "min", "<= result", ">= result", "<==>", "correctresult", "result =="],
        "missing": "formal optimality/argmax/minimality comparison",
    },
    "exact_value_missing": {
        "nl": [r"\bfind\b", r"\bdetermine\b", r"\bcount\b", r"\breturn\b", r"\bcompute\b", r"\bcalculate\b", r"\banswer\b"],
        "strong_spec": ["result ==", "correctresult", "forall", "exists", "<==>", "count", "sum"],
        "missing": "semantic definition of the exact returned value",
    },
    "simulation_semantics_missing": {
        "nl": [r"\bsimulat", r"\bprocess\b", r"\bgame\b", r"\boperation", r"\bturn\b", r"\bstate\b", r"\bsequence\b", r"\brecurr"],
        "strong_spec": ["function ", "predicate ", "decreases", "correctresult", "forall", "exists", "result =="],
        "missing": "transition/process semantics tying result to simulated behavior",
    },
    "conservation_or_permutation_missing": {
        "nl": [r"\bsame elements\b", r"\bsort", r"\brearrang", r"\bpermutation\b", r"\bno loss\b", r"\bno duplication\b", r"\bconserv", r"\bpreserv"],
        "strong_spec": ["multiset", "permutation", "count", "forall", "sum", "old("],
        "missing": "multiset/count/sum preservation or permutation relation",
    },
    "tie_break_missing": {
        "nl": [r"\btie\b", r"\bif multiple\b", r"\bchoose smallest\b", r"\bchoose largest\b", r"\bfirst\b", r"\blast\b"],
        "strong_spec": ["forall", "==>", "<==>", "largest", "smallest", "max", "min"],
        "missing": "specified tie-breaking rule",
    },
    "impossible_case_missing": {
        "nl": [r"\bimpossible\b", r"\bno solution\b", r"\breturn -1\b", r"\bno such\b"],
        "strong_spec": ["<==>", "iff", "==>", "exists", "forall", "result == -1"],
        "missing": "equivalence between impossibility condition and sentinel output",
    },
    "output_format_missing": {
        "nl": [r"\boutput format\b", r"\bprint\b", r"\bnewline\b", r"\bspace-separated\b", r"\border\b", r"\bstring\b"],
        "strong_spec": ["contains", "prefix", "suffix", "substring", "forall", "result =="],
        "missing": "exact output formatting/order/string constraints",
    },
}


def regex_any(patterns: List[str], text: str) -> bool:
    return any(re.search(p, text, flags=re.IGNORECASE) for p in patterns)


def spec_lacks(strong_tokens: List[str], spec_l: str) -> bool:
    return not any(tok.lower() in spec_l for tok in strong_tokens)


def confidence_rank(c: str) -> int:
    return {"high": 3, "medium": 2, "low": 1}.get(c, 0)


def score_candidate(category: str, norm: Dict[str, Any], reasons: List[str]) -> Tuple[str, int]:
    spec = norm.get("spec_full", "")
    base = 0
    if norm.get("source_bucket") == "apps":
        base += 2
    if useful_description(norm):
        base += 2
    if is_trivial_or_shape_only_spec(spec):
        base += 4
        reasons.append("spec appears trivial or shape/range-only")
    if spec_strength_score(spec) <= 2:
        base += 2
        reasons.append("spec has few semantic-strength tokens")
    if category == "trivial_postcondition":
        base += 4
    if base >= 9:
        return "high", base
    if base >= 6:
        return "medium", base
    if base >= 4:
        return "low", base
    return "drop", base


def candidate_bad_behavior(category: str, spec: str) -> str:
    if re.search(r"result\s*>=\s*0|0\s*<=\s*result", spec, flags=re.IGNORECASE):
        return "return 0 or 1 regardless of the input"
    if category == "optimization_missing":
        return "return a feasible but non-optimal value"
    if category == "simulation_semantics_missing":
        return "return a one-step approximation without simulating the process"
    return "return a range/shape-valid but semantically wrong value"


def find_candidates(norm: Dict[str, Any]) -> List[Dict[str, Any]]:
    desc = norm.get("description", "")
    spec = norm.get("spec_full", "")
    desc_l = desc.lower()
    spec_l = spec.lower()
    out = []

    def add(category: str, reasons: List[str]) -> None:
        confidence, numeric = score_candidate(category, norm, reasons)
        if confidence == "drop":
            return
        out.append({
            "id": norm.get("task_id"),
            "source": norm.get("source"),
            "source_bucket": norm.get("source_bucket"),
            "source_id": norm.get("source_id"),
            "gap_category": category,
            "confidence": confidence,
            "score": numeric,
            "nl_excerpt": short_excerpt(desc, 900),
            "spec_excerpt": short_excerpt(spec, 1100),
            "suspected_missing_requirement": CATEGORY_DEFS.get(category, {}).get("missing", "semantic correctness condition"),
            "why_spec_may_be_weak": "; ".join(dict.fromkeys(reasons)),
            "possible_bad_candidate_behavior": candidate_bad_behavior(category, spec),
            "simple_constant_might_satisfy_spec": bool(is_trivial_or_shape_only_spec(spec)),
            "validation_difficulty": "easy" if is_trivial_or_shape_only_spec(spec) else "medium",
            "status": "candidate_only_needs_manual_validation",
        })

    if is_trivial_or_shape_only_spec(spec):
        add("trivial_postcondition", ["formal postcondition appears to contain only weak result/range/shape constraints"])

    for category, cfg in CATEGORY_DEFS.items():
        if regex_any(cfg["nl"], desc_l):
            reasons = [f"NL contains {category.replace('_', ' ')} cues"]
            if spec_lacks(cfg["strong_spec"], spec_l):
                reasons.append(f"spec lacks expected patterns for {cfg['missing']}")
                add(category, reasons)
    return out


def render_markdown(result: Dict[str, Any]) -> str:
    candidates = result.get("candidates", [])
    md = [
        "# External Vericoding Gap Candidates",
        "",
        "All entries are candidate-only and require manual validation.",
        "",
        f"- Records total: **{result.get('records_total')}**",
        f"- Records audited by scanner: **{result.get('records_audited')}**",
        f"- Candidate gaps found: **{result.get('candidate_count')}**",
        "",
        "## Counts by confidence",
        "",
        markdown_table(["Confidence", "Count"], sorted(result.get("candidate_count_by_confidence", {}).items())),
        "",
        "## Counts by category",
        "",
        markdown_table(["Category", "Count"], sorted(result.get("candidate_count_by_category", {}).items())),
        "",
        "## Top 50 candidates",
        "",
    ]
    rows = []
    for c in candidates[:50]:
        rows.append([c.get("id"), c.get("source"), c.get("source_id"), c.get("gap_category"), c.get("confidence"), c.get("validation_difficulty")])
    md.append(markdown_table(["Case", "Source", "Source ID", "Category", "Confidence", "Validation difficulty"], rows))
    for c in candidates[:50]:
        md += [
            "",
            f"### {c.get('id')} - {c.get('confidence')} confidence",
            "",
            f"Source: `{c.get('source')}` / `{c.get('source_id')}`",
            "",
            f"Suspected missing requirement: **{c.get('suspected_missing_requirement')}**",
            "",
            f"Why spec may be weak: {c.get('why_spec_may_be_weak')}",
            "",
            f"Suggested bad candidate: `{c.get('possible_bad_candidate_behavior')}`",
            "",
            "NL excerpt:",
            fenced_excerpt(c.get("nl_excerpt", ""), lang="text"),
            "Spec excerpt:",
            fenced_excerpt(c.get("spec_excerpt", ""), lang="dafny"),
            "",
        ]
    return "\n".join(md)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jsonl-path", type=Path)
    parser.add_argument("--min-qa-score", type=float, default=0.8)
    args = parser.parse_args()

    jsonl_path = args.jsonl_path
    meta = None
    if jsonl_path is None:
        jsonl_path, meta = resolve_dafny_jsonl_path()
    if jsonl_path is None or not jsonl_path.exists():
        write_skipped_report("Cannot scan external benchmark: no supported dafny_tasks.jsonl is available.")
        return 0

    records = load_jsonl(jsonl_path)
    norms = [normalize_record(r) for r in records]
    audited: List[Dict[str, Any]] = []
    candidates: List[Dict[str, Any]] = []
    for n in norms:
        source_bucket = n.get("source_bucket")
        if source_bucket not in {"apps", "humaneval"}:
            continue
        if not useful_description(n):
            continue
        if source_bucket == "apps":
            q = n.get("qa_score_float")
            if q is not None and q < args.min_qa_score:
                continue
        audited.append(n)
        candidates.extend(find_candidates(n))

    dedup: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for c in candidates:
        key = (str(c.get("id")), str(c.get("gap_category")))
        prev = dedup.get(key)
        if prev is None or (confidence_rank(c["confidence"]), c["score"]) > (confidence_rank(prev["confidence"]), prev["score"]):
            dedup[key] = c
    candidates = list(dedup.values())
    candidates.sort(key=lambda c: (-confidence_rank(c["confidence"]), -int(c.get("score", 0)), str(c.get("id")), str(c.get("gap_category"))))

    by_category = defaultdict(int)
    by_confidence = defaultdict(int)
    for c in candidates:
        by_category[c["gap_category"]] += 1
        by_confidence[c["confidence"]] += 1

    result = {
        "status": "candidate_scan_completed",
        "dataset": meta or {"jsonl_path": str(jsonl_path)},
        "jsonl_path": str(jsonl_path),
        "records_total": len(records),
        "records_audited": len(audited),
        "candidate_count": len(candidates),
        "candidate_count_by_category": dict(sorted(by_category.items())),
        "candidate_count_by_confidence": dict(sorted(by_confidence.items())),
        "candidates": candidates,
    }
    write_json(REPORTS / "external_vericoding_gap_candidates.json", result)
    write_text(REPORTS / "external_vericoding_gap_candidates.md", render_markdown(result))
    print(f"Scanned {len(audited)} audit-eligible records; found {len(candidates)} candidate gaps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
