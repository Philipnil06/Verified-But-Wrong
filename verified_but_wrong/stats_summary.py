from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runner import RESULTS_DIR, load_latest_benchmark, run_mini_benchmark
from spec_audit_calibration import load_policy_gate_calibration, run_policy_gate_calibration


STATS_SUMMARY_JSON = RESULTS_DIR / "stats_summary.json"
STATS_SUMMARY_MD = RESULTS_DIR / "stats_summary.md"


def _wilson(successes: int, total: int, z: float = 1.96) -> dict[str, float]:
    if total == 0:
        return {"estimate": 0.0, "low": 0.0, "high": 0.0}
    phat = successes / total
    denom = 1 + z * z / total
    center = (phat + z * z / (2 * total)) / denom
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * total)) / total) / denom
    return {"estimate": phat, "low": max(0.0, center - margin), "high": min(1.0, center + margin)}


def build_stats_summary() -> dict[str, Any]:
    benchmark = load_latest_benchmark() or run_mini_benchmark()
    gate = load_policy_gate_calibration() or run_policy_gate_calibration()
    metrics = gate["metrics"]
    rows = {
        "naive_vbw_rate": _wilson(benchmark["naive"]["wrong_selections"], benchmark["naive"]["total_tasks"]),
        "critic_vbw_rate": _wilson(benchmark["critic"]["wrong_selections"], benchmark["critic"]["total_tasks"]),
        "oracle_vbw_rate": _wilson(benchmark["oracle"]["wrong_selections"], benchmark["oracle"]["total_tasks"]),
        "gate_dangerous_catch_rate": _wilson(metrics["dangerous_caught"], metrics["dangerous_total"]),
        "gate_safe_allow_rate": _wilson(metrics["safe_allowed"], metrics["safe_total"]),
        "high_or_critical_dangerous_catch_rate": _wilson(
            metrics["high_or_critical_dangerous_caught"],
            metrics["high_or_critical_dangerous_total"],
        ),
    }
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "note": "Because the benchmark is controlled and small, intervals are descriptive rather than claims about real-world prevalence.",
        "wilson_95_intervals": rows,
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    STATS_SUMMARY_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    write_stats_summary(result)
    return result


def write_stats_summary(result: dict[str, Any]) -> None:
    lines = [
        "# Descriptive Statistics Summary",
        "",
        "Because the benchmark is controlled and small, intervals are descriptive rather than claims about real-world prevalence.",
        "",
        "| metric | estimate | Wilson low | Wilson high |",
        "|---|---:|---:|---:|",
    ]
    for metric, interval in result["wilson_95_intervals"].items():
        lines.append(
            f"| `{metric}` | {interval['estimate']:.4f} | {interval['low']:.4f} | {interval['high']:.4f} |"
        )
    STATS_SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    print(json.dumps(build_stats_summary(), indent=2, ensure_ascii=False))
