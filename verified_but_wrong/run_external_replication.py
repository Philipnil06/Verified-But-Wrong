#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run_step(cmd: list[str]) -> None:
    p = subprocess.run(cmd, cwd=ROOT, text=True, check=False)
    if p.returncode != 0:
        raise SystemExit(p.returncode)


def ensure_dafny() -> None:
    p = subprocess.run(["dotnet", "tool", "run", "dafny", "--version"], cwd=ROOT, text=True, capture_output=True, check=False)
    if p.returncode != 0:
        raise SystemExit("Dafny not found. Run dotnet tool restore or install Dafny 4.11.0.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-dafny", action="store_true")
    ap.add_argument("--skip-repair", action="store_true")
    ap.add_argument("--skip-random-control", action="store_true")
    args = ap.parse_args()

    run_step([sys.executable, "scripts/external_replication/build_high_confidence_inventory.py"])
    run_step([sys.executable, "scripts/external_replication/adjudicate_high_confidence.py"])

    if not args.skip_dafny:
        ensure_dafny()
        run_step([sys.executable, "scripts/external_replication/run_dafny_external_cases.py"])
    if not args.skip_repair:
        ensure_dafny()
        run_step([sys.executable, "scripts/external_replication/run_repaired_target_checks.py"])

    run_step([sys.executable, "scripts/external_replication/run_intended_examples.py"])
    if not args.skip_random_control:
        run_step([sys.executable, "scripts/external_replication/random_control_sample.py"])
    run_step([sys.executable, "scripts/external_replication/make_external_replication_tables.py"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
