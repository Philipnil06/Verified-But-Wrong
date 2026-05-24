#!/usr/bin/env python3
from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "external_replication"
JSONL = ROOT / "external_data" / "vericoding-benchmark" / "jsonl" / "dafny_tasks.jsonl"
CAND = ROOT / "reports" / "external_vericoding_gap_candidates.json"


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
    tasks = load_jsonl(JSONL)
    cand = json.loads(CAND.read_text(encoding="utf-8"))
    cand_ids = {str(c.get("id")) for c in cand.get("candidates", [])}
    useful = [t for t in tasks if str(t.get("vc-description", "")).strip() and len(str(t.get("vc-description", "")).split()) >= 6]
    pool = [t for t in useful if str(t.get("id")) not in cand_ids]
    rng = random.Random(202605)
    sample = rng.sample(pool, k=min(30, len(pool)))

    rows = [{"case_id": s.get("id"), "source": s.get("source"), "source_id": s.get("source-id"), "label": "unclear", "notes": "quick control slot"} for s in sample]
    with (OUT / "random_control_sample.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    with (OUT / "random_control_adjudication.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    (OUT / "random_control_summary.md").write_text(
        "\n".join([
            "# Optional Control Sample",
            "",
            "- fixed seed: `202605`",
            f"- sampled tasks: {len(rows)}",
            "- labels are placeholders until manual review.",
            "- this is not prevalence evidence.",
        ]) + "\n",
        encoding="utf-8",
    )
    print(f"wrote random control sample: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
