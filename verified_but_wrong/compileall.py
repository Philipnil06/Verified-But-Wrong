from __future__ import annotations

import hashlib
import os
import py_compile
import sys
from pathlib import Path


def _target_pyc(source: Path) -> Path:
    root = Path(os.environ.get("TEMP", "C:\\Temp")) / "verified_but_wrong_compileall"
    root.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha1(str(source.resolve()).encode("utf-8")).hexdigest()
    return root / f"{source.stem}_{digest}.pyc"


def _iter_python_files(root: Path):
    if root.is_file() and root.suffix == ".py":
        yield root
        return
    for path in root.rglob("*.py"):
        if "__pycache__" not in path.parts:
            yield path


def main() -> int:
    roots = [Path(arg) for arg in sys.argv[1:] if not arg.startswith("-")] or [Path(".")]
    failed = False
    for root in roots:
        print(f"Listing '{root}'...")
        for source in _iter_python_files(root):
            try:
                py_compile.compile(str(source), cfile=str(_target_pyc(source)), doraise=True)
            except py_compile.PyCompileError as exc:
                failed = True
                print(exc.msg, file=sys.stderr)
            except OSError as exc:
                failed = True
                print(f"{source}: {exc}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
