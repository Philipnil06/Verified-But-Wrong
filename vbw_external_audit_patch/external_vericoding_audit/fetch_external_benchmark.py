#!/usr/bin/env python3
"""Fetch or register the public external vericoding benchmark data.

Supported layouts:
1. external_data/vericoding-benchmark/jsonl/dafny_tasks.jsonl
2. external_data/vericoding/benchmarks/dafny_tasks.jsonl

The script prefers vericoding-benchmark, then falls back to vericoding, then raw
JSONL URLs. It writes clean skipped reports instead of breaking the whole
reproduction when network is unavailable.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from common import (
    DATASET_VARIANTS,
    REPORTS,
    backup_path,
    dataset_metadata,
    ensure_dirs,
    resolve_dafny_jsonl_path,
    variants_for_repo_arg,
    write_json,
    write_skipped_report,
    write_text,
)


def run(cmd: list[str]) -> Tuple[int, str]:
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False, timeout=45)
        return p.returncode, p.stdout
    except subprocess.TimeoutExpired as e:
        return 124, f"timeout after {e.timeout}s"
    except FileNotFoundError as e:
        return 127, str(e)


def has_jsonl(root: Path, rel: Path) -> bool:
    return (root / rel).exists()


def register_jsonl_path(src: Path, preferred_variant_key: str = "benchmark") -> Dict[str, Any]:
    src = src.resolve()
    variant = next(v for v in DATASET_VARIANTS if v.key == preferred_variant_key)
    dst = variant.jsonl_path
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and src != dst.resolve():
        bak = backup_path(dst)
        shutil.copy2(dst, bak)
    if src != dst.resolve():
        shutil.copy2(src, dst)
    (variant.local_root / "EXTERNAL_COMMIT.txt").write_text("unknown: local JSONL file registered\n", encoding="utf-8")
    return {**dataset_metadata(variant, fetch_method="local_jsonl"), "registered_from": str(src)}


def register_local_path(src: Path, refresh: bool = False) -> Optional[Dict[str, Any]]:
    src = src.resolve()
    if src.is_file():
        return register_jsonl_path(src)
    for variant in DATASET_VARIANTS:
        candidate = src / variant.jsonl_rel
        if candidate.exists():
            target = variant.local_root
            if src == target.resolve():
                return dataset_metadata(variant, fetch_method="local")
            if target.exists():
                if refresh:
                    shutil.rmtree(target)
                elif not variant.jsonl_path.exists():
                    bak = backup_path(target)
                    target.rename(bak)
                else:
                    return dataset_metadata(variant, fetch_method="local_existing")
            shutil.copytree(src, target)
            return dataset_metadata(variant, fetch_method="local_path_copy")
    return None


def prepare_target(target: Path, refresh: bool) -> None:
    if target.exists():
        if refresh:
            shutil.rmtree(target)
            return
        if not any(target.iterdir()):
            target.rmdir()
            return
        # A previous failed clone often leaves a non-empty folder without JSONL.
        # Avoid destroying user data: move it aside once.
        bak = backup_path(target)
        target.rename(bak)


def clone_variant(variant, refresh: bool = False) -> Tuple[bool, Dict[str, Any], str]:
    if variant.jsonl_path.exists() and not refresh:
        return True, dataset_metadata(variant, fetch_method="local"), "reused existing dataset"
    prepare_target(variant.local_root, refresh=refresh)
    rc, out = run(["git", "clone", "--depth", "1", variant.repo_url, str(variant.local_root)])
    if rc != 0:
        return False, dataset_metadata(variant, fetch_method="git_failed"), out
    if not variant.jsonl_path.exists():
        return False, dataset_metadata(variant, fetch_method="git_missing_jsonl"), f"clone succeeded but missing {variant.jsonl_rel}"
    return True, dataset_metadata(variant, fetch_method="git"), out


def raw_download_variant(variant) -> Tuple[bool, Dict[str, Any], str]:
    try:
        variant.jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(variant.raw_url, timeout=30) as response:
            data = response.read()
        variant.jsonl_path.write_bytes(data)
        (variant.local_root / "EXTERNAL_COMMIT.txt").write_text("unknown: raw-file fallback download\n", encoding="utf-8")
        return True, dataset_metadata(variant, fetch_method="raw"), f"downloaded {len(data)} bytes"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return False, dataset_metadata(variant, fetch_method="raw_failed"), str(e)


def render_fetch_md(result: Dict[str, Any]) -> str:
    md = ["# External Vericoding Fetch", "", f"Status: `{result.get('status')}`", ""]
    if result.get("dataset"):
        md += ["## Dataset", "", "```json", json.dumps(result["dataset"], indent=2, ensure_ascii=False), "```", ""]
    if result.get("attempts"):
        md += ["## Attempts", ""]
        for a in result["attempts"]:
            md.append(f"- `{a.get('repo_name')}` via `{a.get('method')}`: {a.get('ok')} — {a.get('message','')[:300]}")
        md.append("")
    return "\n".join(md)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", choices=["auto", "benchmark", "tools"], default="auto")
    parser.add_argument("--refresh", action="store_true", help="Refetch selected external data. Existing folders are only removed when this flag is passed.")
    parser.add_argument("--local-path", type=Path, help="Register or copy a manually downloaded repo/folder containing a supported dafny_tasks.jsonl.")
    parser.add_argument("--jsonl-path", type=Path, help="Register a manually downloaded dafny_tasks.jsonl file.")
    parser.add_argument("--no-raw-fallback", action="store_true")
    args = parser.parse_args()

    ensure_dirs()
    attempts = []

    try:
        if args.jsonl_path:
            if not args.jsonl_path.exists():
                raise FileNotFoundError(args.jsonl_path)
            dataset = register_jsonl_path(args.jsonl_path)
            result = {"status": "available", "dataset": dataset, "attempts": attempts}
            write_json(REPORTS / "external_vericoding_fetch.json", result)
            write_text(REPORTS / "external_vericoding_fetch.md", render_fetch_md(result))
            print(json.dumps(result, indent=2))
            return 0

        if args.local_path:
            if not args.local_path.exists():
                raise FileNotFoundError(args.local_path)
            dataset = register_local_path(args.local_path, refresh=args.refresh)
            if not dataset:
                raise FileNotFoundError(f"No supported dafny_tasks.jsonl found under {args.local_path}")
            result = {"status": "available", "dataset": dataset, "attempts": attempts}
            write_json(REPORTS / "external_vericoding_fetch.json", result)
            write_text(REPORTS / "external_vericoding_fetch.md", render_fetch_md(result))
            print(json.dumps(result, indent=2))
            return 0

        existing, meta = resolve_dafny_jsonl_path()
        if existing and not args.refresh:
            result = {"status": "available", "dataset": meta, "attempts": attempts}
            write_json(REPORTS / "external_vericoding_fetch.json", result)
            write_text(REPORTS / "external_vericoding_fetch.md", render_fetch_md(result))
            print(json.dumps(result, indent=2))
            return 0

        for variant in variants_for_repo_arg(args.repo):
            ok, meta, msg = clone_variant(variant, refresh=args.refresh)
            attempts.append({"repo_name": variant.repo_name, "method": "git", "ok": ok, "message": msg})
            if ok:
                result = {"status": "available", "dataset": meta, "attempts": attempts}
                write_json(REPORTS / "external_vericoding_fetch.json", result)
                write_text(REPORTS / "external_vericoding_fetch.md", render_fetch_md(result))
                print(json.dumps(result, indent=2))
                return 0

        if not args.no_raw_fallback:
            for variant in variants_for_repo_arg(args.repo):
                ok, meta, msg = raw_download_variant(variant)
                attempts.append({"repo_name": variant.repo_name, "method": "raw", "ok": ok, "message": msg})
                if ok:
                    result = {"status": "available", "dataset": meta, "attempts": attempts}
                    write_json(REPORTS / "external_vericoding_fetch.json", result)
                    write_text(REPORTS / "external_vericoding_fetch.md", render_fetch_md(result))
                    print(json.dumps(result, indent=2))
                    return 0

    except Exception as e:
        attempts.append({"repo_name": args.repo, "method": "exception", "ok": False, "message": repr(e)})

    reason = "External vericoding data unavailable after local, git, and raw fallback attempts."
    result = {"status": "skipped", "reason": reason, "attempts": attempts}
    write_json(REPORTS / "external_vericoding_fetch.json", result)
    write_text(REPORTS / "external_vericoding_fetch.md", render_fetch_md(result))
    write_skipped_report(reason, metadata=result)
    print(reason)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
