#!/usr/bin/env python3
"""Conservative helper for copying the external audit patch into a real repo.

Run from the patch folder with the target repo path:

    python integrate_external_vericoding_patch.py /path/to/real/repo

This copies new external audit directories and creates .bak files before touching
existing runner/evidence files. It does not attempt a clever semantic merge.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

PATCH_ROOT = Path(__file__).resolve().parent


def backup(path: Path) -> Path:
    i = 1
    while True:
        b = path.with_name(path.name + f".bak{i}")
        if not b.exists():
            shutil.copy2(path, b)
            return b
        i += 1


def copy_dir(src: Path, dst: Path, overwrite: bool = False) -> str:
    if dst.exists() and not overwrite:
        return f"skipped existing directory {dst}"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    return f"copied {src} -> {dst}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    parser.add_argument("--overwrite-new-dirs", action="store_true")
    args = parser.parse_args()
    repo = args.repo.resolve()
    if not repo.exists():
        raise SystemExit(f"Target repo does not exist: {repo}")

    actions = []
    for rel in ["external_vericoding_audit", "external_vericoding_cases"]:
        actions.append(copy_dir(PATCH_ROOT / rel, repo / rel, overwrite=args.overwrite_new_dirs))

    for rel in ["run_all_repro.py", "analysis/evidence_pack.py", "README_external_vericoding_audit.md"]:
        src = PATCH_ROOT / rel
        dst = repo / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            b = backup(dst)
            actions.append(f"backed up {dst} -> {b}; did not overwrite automatically")
            # write reference version alongside for manual merge
            ref = dst.with_name(dst.name + ".external_vericoding_reference")
            shutil.copy2(src, ref)
            actions.append(f"wrote merge reference {ref}")
        else:
            shutil.copy2(src, dst)
            actions.append(f"copied {src} -> {dst}")

    reports = repo / "reports"
    reports.mkdir(exist_ok=True)
    notes_src = PATCH_ROOT / "reports" / "external_vericoding_integration_notes.md"
    shutil.copy2(notes_src, reports / notes_src.name)
    actions.append(f"copied integration notes to {reports / notes_src.name}")

    print("\n".join(actions))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
