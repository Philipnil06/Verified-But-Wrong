#!/usr/bin/env python3
"""Inspect external Dafny JSONL records for audit viability.

This report is descriptive only. It never claims target-validity gaps by itself.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List

from common import (
    REPORTS,
    field_frequencies,
    fenced_excerpt,
    fenced_json,
    is_trivial_or_shape_only_spec,
    load_jsonl,
    markdown_table,
    normalize_record,
    resolve_dafny_jsonl_path,
    short_excerpt,
    useful_description,
    write_json,
    write_skipped_report,
    write_text,
)


def sample_norms(norms: List[Dict[str, Any]], source: str, limit: int = 10) -> List[Dict[str, Any]]:
    rows = [n for n in norms if n.get("source_bucket") == source]
    rows.sort(key=lambda n: str(n.get("task_id")))
    return [sample_record(n) for n in rows[:limit]]


def sample_record(n: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": n.get("task_id"),
        "source": n.get("source"),
        "source_bucket": n.get("source_bucket"),
        "source_id": n.get("source_id"),
        "qa_score": n.get("qa_score_float"),
        "description_excerpt": short_excerpt(n.get("description", ""), 600),
        "spec_excerpt": short_excerpt(n.get("spec_full", ""), 700),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jsonl-path", type=Path)
    args = parser.parse_args()

    jsonl_path = args.jsonl_path
    meta = None
    if jsonl_path is None:
        jsonl_path, meta = resolve_dafny_jsonl_path()
    if jsonl_path is None or not jsonl_path.exists():
        write_skipped_report("Cannot inspect external benchmark: no supported dafny_tasks.jsonl is available.")
        print("External vericoding inspection skipped: missing JSONL")
        return 0

    records = load_jsonl(jsonl_path)
    norms = [normalize_record(r) for r in records]
    source_counts = Counter(n.get("source_bucket") for n in norms)
    useful_by_source = Counter(n.get("source_bucket") for n in norms if useful_description(n))
    nonempty_desc_by_source = Counter(n.get("source_bucket") for n in norms if n.get("description"))
    missing_field_counts = Counter()
    for n in norms:
        missing_field_counts.update(n.get("missing_canonical_fields", []))

    weakest = [n for n in norms if is_trivial_or_shape_only_spec(n.get("spec_full", ""))]
    weakest.sort(key=lambda n: (n.get("source_bucket") != "apps", str(n.get("task_id"))))

    apps_total = source_counts.get("apps", 0)
    humaneval_total = source_counts.get("humaneval", 0)
    apps_useful = useful_by_source.get("apps", 0)
    humaneval_useful = useful_by_source.get("humaneval", 0)
    recommended = [
        n for n in norms
        if n.get("source_bucket") == "apps" and useful_description(n) and (n.get("qa_score_float") is None or n.get("qa_score_float") >= 0.8)
    ]

    result: Dict[str, Any] = {
        "status": "inspected",
        "dataset": meta or {"jsonl_path": str(jsonl_path)},
        "jsonl_path": str(jsonl_path),
        "total_records": len(records),
        "observed_fields": dict(sorted(field_frequencies(records).items())),
        "fields_observed": dict(sorted(field_frequencies(records).items())),
        "records_with_id": sum(1 for n in norms if n.get("task_id")),
        "records_with_description": sum(1 for n in norms if n.get("description")),
        "records_with_spec": sum(1 for n in norms if n.get("spec_full")),
        "records_with_useful_description": sum(1 for n in norms if useful_description(n)),
        "missing_canonical_fields": dict(sorted(missing_field_counts.items())),
        "counts_by_source": dict(sorted(source_counts.items())),
        "by_source": dict(sorted(source_counts.items())),
        "useful_description_counts_by_source": dict(sorted(useful_by_source.items())),
        "nonempty_descriptions_by_source": dict(sorted(nonempty_desc_by_source.items())),
        "useful_descriptions_by_source": dict(sorted(useful_by_source.items())),
        "total_with_nonempty_description": sum(1 for n in norms if n.get("description")),
        "total_with_useful_description": sum(1 for n in norms if useful_description(n)),
        "total_apps_records": apps_total,
        "total_apps_useful_descriptions": apps_useful,
        "total_humaneval_records": humaneval_total,
        "total_humaneval_useful_descriptions": humaneval_useful,
        "total_dafnybench_records": source_counts.get("dafnybench", 0),
        "total_dafnybench_useful_descriptions": useful_by_source.get("dafnybench", 0),
        "total_bignum_records": source_counts.get("bignum", 0),
        "total_bignum_useful_descriptions": useful_by_source.get("bignum", 0),
        "recommended_subset": {
            "source": "apps",
            "filter": "useful vc-description and qa-score >= 0.8 when qa-score is available",
            "count": len(recommended),
        },
        "samples": {
            "apps": sample_norms(norms, "apps", 10),
            "humaneval": sample_norms(norms, "humaneval", 10),
            "weakest_spec_looking": [sample_record(n) for n in weakest[:10]],
        },
        "framing": "Inspection report only. It makes no target-validity or prevalence claim.",
    }

    write_json(REPORTS / "external_vericoding_inspection.json", result)
    write_text(REPORTS / "external_vericoding_inspection.md", render_markdown(result))
    print(f"Inspected {len(records)} records from {jsonl_path}")
    return 0


def render_markdown(result: Dict[str, Any]) -> str:
    md = [
        "# External Vericoding Inspection",
        "",
        "This report checks whether the public Dafny JSONL is viable for target-validity auditing. It does not validate gaps or estimate prevalence.",
        "",
        "## Dataset",
        "",
        fenced_json(result.get("dataset", {})),
        "",
        "## Counts",
        "",
        f"- Total records: **{result['total_records']}**",
        f"- Total with non-empty description: **{result['total_with_nonempty_description']}**",
        f"- Total with useful description: **{result['total_with_useful_description']}**",
        f"- APPS records: **{result['total_apps_records']}**",
        f"- APPS useful descriptions: **{result['total_apps_useful_descriptions']}**",
        f"- HumanEval records: **{result['total_humaneval_records']}**",
        f"- HumanEval useful descriptions: **{result['total_humaneval_useful_descriptions']}**",
        "",
        "### By source",
        "",
        markdown_table(["Source", "Records", "Non-empty descriptions", "Useful descriptions"], [
            [src, result.get("by_source", {}).get(src, 0), result.get("nonempty_descriptions_by_source", {}).get(src, 0), result.get("useful_descriptions_by_source", {}).get(src, 0)]
            for src in sorted(set(result.get("by_source", {})) | set(result.get("useful_descriptions_by_source", {})))
        ]),
        "",
        "## Fields observed",
        "",
        markdown_table(["Field", "Frequency"], sorted(result.get("fields_observed", {}).items())),
        "",
        "## Missing canonical fields",
        "",
        markdown_table(["Canonical field", "Missing count"], sorted(result.get("missing_canonical_fields", {}).items())),
        "",
        "## Recommended subset for audit",
        "",
        f"Use APPS tasks with useful descriptions and qa-score >= 0.8 when qa-score is available. Count: **{result['recommended_subset']['count']}**.",
        "",
    ]
    for section in ["apps", "humaneval", "weakest_spec_looking"]:
        md += [f"## Sample {section} records", ""]
        for sample in result.get("samples", {}).get(section, []):
            md += [
                f"### {sample.get('id')} ({sample.get('source')})",
                "",
                f"Source id: `{sample.get('source_id')}`",
                "",
                "NL excerpt:",
                fenced_excerpt(sample.get("description_excerpt", ""), lang="text"),
                "Spec excerpt:",
                fenced_excerpt(sample.get("spec_excerpt", ""), lang="dafny"),
                "",
            ]
    return "\n".join(md)


if __name__ == "__main__":
    raise SystemExit(main())
