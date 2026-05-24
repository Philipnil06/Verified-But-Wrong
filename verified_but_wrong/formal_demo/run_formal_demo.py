from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from analysis.common import REPORTS_DIR, timestamp, write_json, write_markdown


FORMAL_DEMO_DIR = Path(__file__).resolve().parent
FORMAL_DEMO_JSON = REPORTS_DIR / "formal_demo_result.json"
FORMAL_DEMO_MD = REPORTS_DIR / "formal_demo_result.md"
PAPER_INSERT_MD = REPORTS_DIR / "paper_insert_formal_demo.md"
CHECKS = [
    {
        "name": "public_impl_verifies",
        "file": "impl_verified_against_public.dfy",
        "contract": "public",
        "expected_outcome": "pass",
    },
    {
        "name": "incomplete_impl_against_intended_fails",
        "file": "impl_fails_intended_contract.dfy",
        "contract": "intended",
        "expected_outcome": "fail",
    },
    {
        "name": "repaired_impl_verifies",
        "file": "repaired_impl.dfy",
        "contract": "intended",
        "expected_outcome": "pass",
    },
]


def _find_dafny() -> str | None:
    direct = shutil.which("dafny")
    if direct:
        return direct
    candidates = [
        Path.home() / ".dotnet" / "tools" / "dafny.exe",
        Path.home() / ".dotnet" / "tools" / "dafny",
        Path("C:/Program Files/Dafny/dafny.exe"),
        Path("C:/Program Files/Dafny/dafny/dafny.exe"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None


def _run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=FORMAL_DEMO_DIR,
        capture_output=True,
        text=True,
        check=False,
    )


def _version_string(dafny_path: str) -> str | None:
    for command in ([dafny_path, "--version"], [dafny_path, "/version"]):
        try:
            proc = _run_command(command)
        except Exception:
            continue
        output = (proc.stdout or proc.stderr).strip()
        if output:
            return output.splitlines()[0]
    return None


def _run_check(dafny_path: str, check: dict[str, str]) -> dict[str, Any]:
    file_path = FORMAL_DEMO_DIR / check["file"]
    attempts = [
        [dafny_path, "verify", str(file_path)],
        [dafny_path, str(file_path)],
    ]
    chosen_command = attempts[0]
    start = time.perf_counter()
    proc = None
    for index, command in enumerate(attempts):
        chosen_command = command
        proc = _run_command(command)
        if index == 0 and proc.returncode != 0:
            error_text = f"{proc.stdout}\n{proc.stderr}".lower()
            if "unknown command" in error_text or "unrecognized" in error_text or "unexpected argument" in error_text:
                continue
        break
    duration_seconds = time.perf_counter() - start
    actual_outcome = "pass" if proc and proc.returncode == 0 else "fail"
    expected_pass = check["expected_outcome"] == "pass"
    observed_expected_failure = check["expected_outcome"] == "fail" and actual_outcome == "fail"
    return {
        "name": check["name"],
        "file": check["file"],
        "contract": check["contract"],
        "command": chosen_command,
        "expected_outcome": check["expected_outcome"],
        "actual_outcome": actual_outcome,
        "result": "PASS" if (actual_outcome == "pass") == expected_pass else ("PASS" if observed_expected_failure else "FAIL"),
        "return_code": proc.returncode if proc else None,
        "duration_seconds": duration_seconds,
        "stdout_excerpt": (proc.stdout or "").strip()[:1000] if proc else "",
        "stderr_excerpt": (proc.stderr or "").strip()[:1000] if proc else "",
    }


def _write_reports(result: dict[str, Any]) -> None:
    lines = [
        "# Formal Demo Result",
        "",
        "This is a tiny illustrative Dafny demo, not an integration of the full benchmark with a proof assistant.",
        "",
        f"- status: `{result['status']}`",
        f"- dafny found: `{result['dafny_found']}`",
        f"- dafny version: `{result.get('dafny_version') or 'unknown'}`",
        "",
        "| Check | Contract | Expected | Result |",
        "|---|---|---|---|",
    ]
    if result["checks"]:
        for check in result["checks"]:
            label = "verifies" if check["expected_outcome"] == "pass" else "fails verification"
            outcome = "PASS" if check["result"] == "PASS" else "FAIL"
            if check["expected_outcome"] == "fail" and check["actual_outcome"] == "fail":
                outcome = "PASS, expected failure observed"
            lines.append(f"| {check['name']} | `{check['contract']}` | {label} | {outcome} |")
    else:
        lines.append("| No checks run | - | - | - |")
    lines.extend(["", "## Interpretation", ""])
    lines.append(result["summary"])
    lines.extend(["", "## Limitations", ""])
    for caveat in result["caveats"]:
        lines.append(f"- {caveat}")
    if not result["dafny_found"]:
        lines.extend(
            [
                "",
                "## Run Instructions",
                "",
                "- Install Dafny and ensure `dafny` is on `PATH`.",
                "- Run `python formal_demo/run_formal_demo.py`.",
                "- Or verify the files directly with `dafny verify formal_demo/impl_verified_against_public.dfy`, `dafny verify formal_demo/impl_fails_intended_contract.dfy`, and `dafny verify formal_demo/repaired_impl.dfy`.",
            ]
        )
    write_markdown(FORMAL_DEMO_MD, "\n".join(lines))

    if result["status"] == "passed":
        insert_lines = [
            "The formal demo illustrates the same target-validity problem in contract form: verification against an incomplete postcondition can succeed even though the implementation violates the intended stronger contract.",
            "",
            "| Check | Contract | Expected | Result |",
            "|---|---|---|---|",
        ]
        for check in result["checks"]:
            label = "verifies" if check["expected_outcome"] == "pass" else "fails verification"
            outcome = "PASS" if check["result"] == "PASS" else "FAIL"
            if check["expected_outcome"] == "fail" and check["actual_outcome"] == "fail":
                outcome = "PASS, expected failure observed"
            insert_lines.append(f"| {check['name']} | `{check['contract']}` | {label} | {outcome} |")
        insert_lines.extend(
            [
                "",
                "Limitations: this is a tiny illustrative Dafny demo, not an integration of the full benchmark with a proof assistant.",
            ]
        )
    else:
        insert_lines = [
            "A tiny formal-contract demo is included, but this repository does not currently have runnable Dafny evidence on this machine.",
            f"Status: `{result['status']}`.",
            "Do not cite this as executed formal evidence unless the Dafny checks are actually run and saved.",
        ]
    write_markdown(PAPER_INSERT_MD, "\n".join(insert_lines))


def run_formal_demo() -> dict[str, Any]:
    dafny_path = _find_dafny()
    if not dafny_path:
        result = {
            "result_type": "formal_demo",
            "timestamp": timestamp(),
            "status": "skipped_dafny_not_installed",
            "dafny_found": False,
            "dafny_version": None,
            "checks": [],
            "summary": "Dafny was not found on PATH, so the illustrative contract demo was not executed.",
            "caveats": [
                "This machine does not currently have Dafny installed or discoverable on PATH.",
                "The reproduction script treats this as a soft skip.",
            ],
        }
        write_json(FORMAL_DEMO_JSON, result)
        _write_reports(result)
        return result

    checks = [_run_check(dafny_path, check) for check in CHECKS]
    all_expected = all(check["result"] == "PASS" for check in checks)
    result = {
        "result_type": "formal_demo",
        "timestamp": timestamp(),
        "status": "passed" if all_expected else "failed_unexpected_outcome",
        "dafny_found": True,
        "dafny_version": _version_string(dafny_path),
        "checks": checks,
        "summary": (
            "The formal demo shows that an implementation can verify against an incomplete public contract, "
            "fail verification against the stronger intended contract, and then verify again after the downgrade invalidation rule is added."
            if all_expected
            else "At least one Dafny check did not produce the expected pass/fail outcome."
        ),
        "caveats": [
            "This is a tiny illustrative Dafny demo, not an integration of the full benchmark with a proof assistant.",
            "The model intentionally focuses on one role-downgrade/session-invalidation invariant.",
        ],
    }
    write_json(FORMAL_DEMO_JSON, result)
    _write_reports(result)
    return result


if __name__ == "__main__":
    print(json.dumps(run_formal_demo(), indent=2, ensure_ascii=False))
