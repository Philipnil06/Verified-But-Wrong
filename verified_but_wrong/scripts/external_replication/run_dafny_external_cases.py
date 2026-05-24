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
    verified_count = 1 if "verified" in out.lower() and p.returncode == 0 else 0
    error_count = out.lower().count("error")
    success = p.returncode == 0
    log_path = LOGS / f"{case_id}_original_target.log"
    log_path.write_text(out, encoding="utf-8")
    return {
        "case_id": case_id,
        "file": str(path),
        "command": " ".join(cmd),
        "exit_code": p.returncode,
        "wall_time_sec": round(wall, 3),
        "verified_count": verified_count,
        "error_count": error_count,
        "success": success,
        "log_path": str(log_path),
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    paths = sorted(CASES.glob("candidate_*/dafny_direct/bad_candidate.dfy"))
    if not paths:
        raise SystemExit("No direct Dafny case files found")

    rows = []
    for p in paths:
        case_id = p.parts[-3].replace("candidate_", "")
        rows.append(run_verify(case_id, p))

    with (OUT / "dafny_direct_summary.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    with (OUT / "dafny_direct_summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    md = ["# Direct-Dafny Summary", "", "| Case | Success | Exit | Log |", "|---|---|---:|---|"]
    for r in rows:
        md.append(f"| {r['case_id']} | {r['success']} | {r['exit_code']} | `{r['log_path']}` |")
    (OUT / "dafny_direct_summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"verified direct-Dafny cases: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
