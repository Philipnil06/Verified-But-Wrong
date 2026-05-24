from __future__ import annotations

import argparse
import json
from pathlib import Path

from runner import run_mini_benchmark


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", default="controlled")
    parser.add_argument("--out", default="results/controlled_benchmark_latest.json")
    args = parser.parse_args()
    result = run_mini_benchmark()
    Path(args.out).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
