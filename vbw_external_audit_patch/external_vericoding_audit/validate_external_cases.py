#!/usr/bin/env python3
"""Execute manually validated external vericoding demonstration cases.

No case is treated as validated unless a human has explicitly marked it as such
in per-case manual_validation.json or external_vericoding_cases/validated_cases.json.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import CASES, REPORTS, fenced_json, markdown_table, safe_case_id, write_json, write_text


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def discover_manual_cases(manifest: Optional[Path]) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    if manifest and manifest.exists():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if isinstance(data, list):
            for row in data:
                if row.get("status") == "validated":
                    task_id = str(row.get("id") or row.get("task_id"))
                    row = dict(row)
                    row["id"] = task_id
                    row["case_dir"] = str(CASES / f"candidate_{safe_case_id(task_id)}")
                    entries.append(row)
    for mv in sorted(CASES.glob("candidate_*/manual_validation.json")):
        data = json.loads(mv.read_text(encoding="utf-8"))
        if data.get("status") == "validated":
            case_dir = mv.parent
            task_id = data.get("id") or case_dir.name.replace("candidate_", "", 1)
            data["id"] = task_id
            data["case_dir"] = str(case_dir)
            entries.append(data)
    out: Dict[str, Dict[str, Any]] = {}
    for e in entries:
        key = str(e.get("case_dir") or e.get("id"))
        out[key] = e
    return list(out.values())


def require_files(case_dir: Path) -> List[str]:
    required = ["source_record.json", "gap_analysis.md", "manual_validation.json", "bad_candidate.py", "intended_oracle.py"]
    return [name for name in required if not (case_dir / name).exists()]


def run_case(entry: Dict[str, Any]) -> Dict[str, Any]:
    case_dir = Path(entry.get("case_dir") or CASES / f"candidate_{safe_case_id(str(entry.get('id')))}")
    missing = require_files(case_dir)
    manual_path = case_dir / "manual_validation.json"
    manual = json.loads(manual_path.read_text(encoding="utf-8")) if manual_path.exists() else {}
    if manual.get("status") != "validated":
        return {**entry, "status": "rejected_by_validator", "error": "manual_validation.json missing or status != validated", "verified_but_wrong_demo": False}
    if missing:
        return {**entry, "status": "incomplete_validated_case", "case_dir": str(case_dir), "missing_files": missing, "verified_but_wrong_demo": False}

    result: Dict[str, Any] = {**entry, **manual, "case_dir": str(case_dir), "status": "validated_manual_entry"}
    sys.path.insert(0, str(case_dir))
    try:
        bad_mod = load_module(f"bad_candidate_{safe_case_id(str(entry.get('id')))}", case_dir / "bad_candidate.py")
        oracle_mod = load_module(f"intended_oracle_{safe_case_id(str(entry.get('id')))}", case_dir / "intended_oracle.py")
        candidate = getattr(bad_mod, "candidate", None)
        if candidate is None:
            raise RuntimeError("bad_candidate.py must define candidate")

        weak_results = None
        weak_pass = None
        demo_type = "manual_proxy_plus_python_oracle"
        weak_path = case_dir / "weak_spec_proxy.py"
        if weak_path.exists():
            weak_mod = load_module(f"weak_spec_proxy_{safe_case_id(str(entry.get('id')))}", weak_path)
            if not hasattr(weak_mod, "run_tests"):
                raise RuntimeError("weak_spec_proxy.py exists but does not define run_tests(candidate)")
            weak_results = weak_mod.run_tests(candidate)
            weak_pass = all(bool(r.get("weak_spec_proxy_pass")) for r in weak_results)
            demo_type = "fully_executable_proxy_plus_python_oracle"
        else:
            weak_pass = manual.get("weak_spec_proxy_pass") is True

        if not hasattr(oracle_mod, "run_tests"):
            raise RuntimeError("intended_oracle.py must define run_tests(candidate)")
        oracle_results = oracle_mod.run_tests(candidate)
        intended_oracle_pass = all(bool(r.get("intended_oracle_pass")) for r in oracle_results)
        any_oracle_fail = any(r.get("intended_oracle_pass") is False for r in oracle_results)
        vbw = bool(weak_pass is True and any_oracle_fail and manual.get("status") == "validated")
        result.update({
            "demo_type": demo_type,
            "weak_spec_proxy_pass": weak_pass,
            "intended_oracle_pass": intended_oracle_pass,
            "verified_but_wrong_demo": vbw,
            "weak_spec_proxy_results": weak_results,
            "intended_oracle_results": oracle_results,
            "framing": "minimal executable/adapted demonstration of the gap; not full Dafny re-verification unless separately implemented",
        })
    except Exception as exc:
        result.update({"status": "execution_error", "error": repr(exc), "verified_but_wrong_demo": False})
    finally:
        try:
            sys.path.remove(str(case_dir))
        except ValueError:
            pass
    return result


def generate_paper_insert(validation_result: Dict[str, Any]) -> None:
    demos = [c for c in validation_result.get("validated_cases", []) if c.get("verified_but_wrong_demo") is True]
    if len(demos) < 3:
        text = "\n".join([
            "# External Vericoding Benchmark Audit — Not Paper-Ready Yet",
            "",
            f"Validated verified-but-wrong demos: **{len(demos)}**.",
            "",
            "This external audit should not be presented as a paper-ready results section until at least 3 manually defensible cases are validated.",
            "",
            "## Next steps",
            "",
            "1. Review `reports/external_vericoding_gap_candidates.md` and choose 3–5 strong cases.",
            "2. For each case, inspect the full NL/source intent and Dafny spec.",
            "3. Write `manual_validation.json`, `bad_candidate.py`, `weak_spec_proxy.py` if executable, and task-specific `intended_oracle.py`.",
            "4. Re-run `python external_vericoding_audit/validate_external_cases.py`.",
            "",
            "## Cautious interpretation",
            "",
            "Candidate gaps are not benchmark bug claims, vulnerability claims, or prevalence estimates.",
        ])
    else:
        rows = []
        for c in demos:
            rows.append([
                c.get("id"), c.get("gap_category"), c.get("nl_requirement"), c.get("formal_spec_gap"), c.get("bad_candidate_behavior"), c.get("demo_type"), c.get("verified_but_wrong_demo"),
            ])
        text = "\n".join([
            "# External Vericoding Benchmark Audit",
            "",
            "We audited paired natural-language descriptions and Dafny specifications from a public vericoding benchmark. We treated the natural-language description as the source-intent artifact and the Dafny specification as the formal selection target. We then searched for target-validity gaps where the formal target appeared weaker than the natural-language intent.",
            "",
            "## Method",
            "",
            "The audit compares `vc-description` against `vc-spec` and `vc-preamble`, generates candidate target-validity gaps, and manually validates the strongest cases through adapted executable demonstrations.",
            "",
            "## Validated cases",
            "",
            markdown_table(["Case", "Gap category", "NL requirement", "Formal spec gap", "Bad candidate", "Demo type", "VBW demo"], rows),
            "",
            "## Cautious interpretation",
            "",
            "We do not claim to reproduce benchmark failures or invalidate the benchmark. We use the paired NL descriptions and Dafny specifications as externally sourced artifacts for target-validity auditing.",
            "",
            "## Limitations",
            "",
            "Manual validation; APPS/HumanEval-focused scan; Python proxy demonstrations unless full Dafny verification is separately implemented; not a prevalence estimate; not a claim that benchmark authors made errors.",
        ])
    write_text(REPORTS / "paper_insert_external_vericoding_audit.md", text + "\n")


def render_markdown(result: Dict[str, Any]) -> str:
    if result.get("status") == "no_validated_cases":
        return "# External Vericoding Validated Cases\n\nNo manually validated cases were found. External audit is not paper-ready yet.\n"
    rows = []
    for c in result.get("validated_cases", []):
        rows.append([
            c.get("id"),
            c.get("source", ""),
            c.get("gap_category", ""),
            c.get("nl_requirement", ""),
            c.get("formal_spec_gap", ""),
            c.get("bad_candidate_behavior", ""),
            c.get("demo_type", ""),
            c.get("weak_spec_proxy_pass"),
            c.get("intended_oracle_pass"),
            c.get("verified_but_wrong_demo"),
        ])
    md = [
        "# External Vericoding Validated Cases",
        "",
        "Rows appear here only after manual validation. These are adapted demonstrations, not full Dafny reproductions unless separately implemented.",
        "",
        markdown_table(["Case", "Source", "Gap category", "NL requirement", "Formal spec gap", "Bad candidate", "Demo type", "Weak spec proxy", "Intended oracle", "VBW demo"], rows),
        "",
    ]
    for c in result.get("validated_cases", []):
        md += [f"## {c.get('id')}", "", fenced_json(c), ""]
    return "\n".join(md)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=CASES / "validated_cases.json")
    args = parser.parse_args()

    entries = discover_manual_cases(args.manifest if args.manifest.exists() else None)
    if not entries:
        result = {"status": "no_validated_cases", "validated_case_count": 0, "verified_but_wrong_demo_count": 0, "validated_cases": []}
        write_json(REPORTS / "external_vericoding_validated_cases.json", result)
        write_text(REPORTS / "external_vericoding_validated_cases.md", render_markdown(result))
        generate_paper_insert(result)
        print("No manually validated external cases found")
        return 0

    rows = [run_case(e) for e in entries]
    vbw_count = sum(1 for r in rows if r.get("verified_but_wrong_demo") is True)
    result = {
        "status": "validated_cases_executed",
        "validated_case_count": len(rows),
        "verified_but_wrong_demo_count": vbw_count,
        "paper_ready": vbw_count >= 3,
        "validated_cases": rows,
    }
    write_json(REPORTS / "external_vericoding_validated_cases.json", result)
    write_text(REPORTS / "external_vericoding_validated_cases.md", render_markdown(result))
    generate_paper_insert(result)
    print(f"Executed {len(rows)} manually validated cases; VBW demos: {vbw_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
