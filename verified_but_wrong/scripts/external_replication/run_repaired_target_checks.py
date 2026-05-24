#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "external_vericoding_cases"
OUT = ROOT / "results" / "external_replication"
LOGS = OUT / "dafny_logs"


def run_verify(case_id: str, path: Path):
    cmd = ["dotnet", "tool", "run", "dafny", "verify", str(path)]
    start = time.time()
    p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False, env=dict(os.environ))
    wall = time.time() - start
    out = (p.stdout or "") + "\n" + (p.stderr or "")
    log_path = LOGS / f"{case_id}_repaired_target.log"
    log_path.write_text(out, encoding="utf-8")
    return {
        "case_id": case_id,
        "file": str(path),
        "command": " ".join(cmd),
        "exit_code": p.returncode,
        "wall_time_sec": round(wall, 3),
        "repaired_target_status": "blocks_bad_candidate" if p.returncode != 0 else "does_not_block",
        "log_path": str(log_path),
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    paths = sorted(CASES.glob("candidate_*/dafny_repaired/bad_candidate_repaired_target.dfy"))
    rows = [run_verify(p.parts[-3].replace("candidate_", ""), p) for p in paths]

    with (OUT / "repaired_target_summary.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    with (OUT / "repaired_target_summary.csv").open("w", newline="", encoding="utf-8") as f:
        if rows:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    md = ["# Repaired-Target Summary", "", "| Case | Repaired Status | Exit | Log |", "|---|---|---:|---|"]
    for r in rows:
        md.append(f"| {r['case_id']} | {r['repaired_target_status']} | {r['exit_code']} | `{r['log_path']}` |")
    (OUT / "repaired_target_summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"checked repaired-target cases: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
