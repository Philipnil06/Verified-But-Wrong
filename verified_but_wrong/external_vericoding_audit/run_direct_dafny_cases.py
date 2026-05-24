#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from common import REPORTS, load_jsonl, write_json, write_text

ROOT = Path(__file__).resolve().parents[1]
JSONL = ROOT / "external_data" / "vericoding-benchmark" / "jsonl" / "dafny_tasks.jsonl"
CASES = ROOT / "external_vericoding_cases"
LOCAL_Z3 = ROOT / ".tools" / "z3" / "z3-4.12.1-x64-win" / "bin"


def find_record(task_id: str) -> Dict[str, Any] | None:
    if not JSONL.exists():
        return None
    for rec in load_jsonl(JSONL):
        if str(rec.get("id", "")).strip() == task_id:
            return rec
    return None


def ensure_case_dir(task_id: str) -> Path:
    d = CASES / f"candidate_{task_id}" / "dafny_direct"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_cmd(args: list[str]) -> Dict[str, Any]:
    try:
        env = dict(**os.environ)
        if LOCAL_Z3.exists():
            env["PATH"] = str(LOCAL_Z3) + os.pathsep + env.get("PATH", "")
        p = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False, env=env)
        return {"command": " ".join(args), "returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr, "not_found": False}
    except FileNotFoundError as e:
        return {"command": " ".join(args), "returncode": 127, "stdout": "", "stderr": str(e), "not_found": True}


def dafny_invocations(target_file: Path) -> list[list[str]]:
    return [
        ["dotnet", "tool", "run", "dafny", "--version"],
        ["dotnet", "tool", "run", "dafny", "verify", str(target_file)],
        ["dotnet", "tool", "run", "dafny", str(target_file)],
        ["dafny", "--version"],
        ["dafny", "verify", str(target_file)],
        ["dafny", str(target_file)],
    ]


def patch_solve_method(spec: str, return_expr: str) -> str:
    marker = "method solve"
    idx = spec.find(marker)
    if idx < 0:
        return spec
    tail = spec[idx:]
    nl = tail.find("\n")
    if nl < 0:
        return spec
    header = tail[:nl]
    body = "{\n  return " + return_expr + ";\n}\n"
    return spec[:idx] + header + "\n" + body


def build_bad_dafny(task_id: str, rec: Dict[str, Any]) -> str:
    pre = str(rec.get("vc-preamble") or "")
    spec = str(rec.get("vc-spec") or "")
    if task_id in {"DA0003", "DA0208"}:
        patched = patch_solve_method(spec, "0")
    else:
        patched = spec
    return (pre.strip() + "\n\n" + patched.strip() + "\n").strip() + "\n"


def intended_examples_result(task_id: str) -> Dict[str, Any]:
    if task_id == "DA0003":
        examples = [
            {"input": [5, 2, 3, 4, 5], "expected": 13},
            {"input": [10, 2, 5, 3, 8], "expected": 28},
            {"input": [12, 3, 4, 7, 2], "expected": 32},
        ]
        rows = []
        for e in examples:
            rows.append({**e, "actual_bad_candidate": 0, "pass": 0 == e["expected"]})
        return {"task_id": task_id, "rows": rows, "all_pass": all(r["pass"] for r in rows)}
    if task_id == "DA0208":
        examples = [
            {"input": [3, 2, [2, 3, 5]], "expected": 5},
            {"input": [4, 2, [1, 2, 7, 9]], "expected": 10},
            {"input": [5, 3, [1, 1, 1, 1, 10]], "expected": 10},
        ]
        rows = []
        for e in examples:
            rows.append({**e, "actual_bad_candidate": 0, "pass": 0 == e["expected"]})
        return {"task_id": task_id, "rows": rows, "all_pass": all(r["pass"] for r in rows)}
    return {"task_id": task_id, "rows": [], "all_pass": False}


def evaluate_case(task_id: str) -> Dict[str, Any]:
    case_dir = ensure_case_dir(task_id)
    rec = find_record(task_id)
    if rec is None:
        result = {"task_id": task_id, "status": "reconstruction_failed", "reason": f"Record not found in {JSONL}"}
        write_json(case_dir / "verify_result.json", result)
        return result

    write_json(case_dir / "original_record.json", rec)
    write_text(case_dir / "original_vc_description.md", str(rec.get("vc-description") or ""))
    write_text(case_dir / "original_vc_preamble.dfy", str(rec.get("vc-preamble") or ""))
    write_text(case_dir / "original_vc_spec.dfy", str(rec.get("vc-spec") or ""))

    bad = build_bad_dafny(task_id, rec)
    bad_path = case_dir / "bad_candidate.dfy"
    write_text(bad_path, bad)

    attempts = []
    version_info = None
    for cmd in dafny_invocations(bad_path):
        out = run_cmd(cmd)
        attempts.append(out)
        if cmd[-1] == "--version" and out["returncode"] == 0:
            version_info = out.get("stdout", "").strip()
            continue
        if "verify" in cmd or (len(cmd) >= 2 and cmd[-1] == str(bad_path)):
            if not out["not_found"]:
                chosen = out
                break
    else:
        chosen = attempts[-1]

    verify_attempts = attempts
    write_text(case_dir / "verify_command.txt", chosen["command"] + "\n")
    write_text(case_dir / "verify_stdout.txt", chosen["stdout"] or "")
    write_text(case_dir / "verify_stderr.txt", chosen["stderr"] or "")
    write_json(case_dir / "verify_attempts.json", verify_attempts)

    examples = intended_examples_result(task_id)
    write_json(case_dir / "intended_examples_result.json", examples)

    if all(a["not_found"] for a in verify_attempts):
        status = "dafny_not_installed"
    elif chosen["returncode"] == 0 and not examples["all_pass"]:
        status = "direct_dafny_verified_and_intent_failed"
    else:
        status = "direct_dafny_failed"

    result = {
        "task_id": task_id,
        "status": status,
        "jsonl_path": str(JSONL),
        "dafny_version": version_info,
        "verify_command": chosen["command"],
        "verify_returncode": chosen["returncode"],
        "intended_examples_all_pass": examples["all_pass"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    write_json(case_dir / "verify_result.json", result)
    write_text(
        case_dir / "README.md",
        "\n".join(
            [
                f"# Direct Dafny Attempt: {task_id}",
                "",
                f"- status: `{status}`",
                f"- verify command: `{chosen['command']}`",
                f"- verify return code: `{chosen['returncode']}`",
                "- direct-dafny claims are made only when verifier return code is 0 and intended examples fail.",
                "",
            ]
        ),
    )
    return result


def render_report(rows: list[Dict[str, Any]]) -> str:
    lines = [
        "# External Vericoding Direct Dafny Attempts",
        "",
        f"- dataset: `{JSONL}`",
        "",
        "| Case | Status | Verify command | Return code | Intended examples all pass |",
        "|---|---|---|---:|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r.get('task_id')} | {r.get('status')} | `{r.get('verify_command','')}` | {r.get('verify_returncode','')} | {r.get('intended_examples_all_pass')} |"
        )
    lines.extend(
        [
            "",
            "Caveat: this report does not claim benchmark bugs, vulnerabilities, or prevalence.",
            "Direct-Dafny claims are emitted only when Dafny verification actually succeeds.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    rows = [evaluate_case("DA0003"), evaluate_case("DA0208")]
    dotnet_probe = run_cmd(["dotnet", "tool", "run", "dafny", "--version"])
    dafny_probe = run_cmd(["dafny", "--version"])
    out = {
        "status": "completed",
        "cases": rows,
        "dafny_available": shutil.which("dafny") is not None or dotnet_probe.get("returncode") == 0,
        "dotnet_tool_dafny_probe": dotnet_probe,
        "dafny_path_probe": dafny_probe,
    }
    write_json(REPORTS / "external_vericoding_direct_dafny.json", out)
    write_text(REPORTS / "external_vericoding_direct_dafny.md", render_report(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
