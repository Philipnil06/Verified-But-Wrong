from __future__ import annotations

import os
import sys
from pathlib import Path


# The hackathon workspace may live under a long OneDrive path on Windows.
# Redirecting bytecode avoids compileall failures when CPython creates temp
# .pyc files for intentionally long candidate filenames.
if os.name == "nt" and sys.pycache_prefix is None:
    pycache_root = Path(os.environ.get("TEMP", "C:\\Temp")) / "verified_but_wrong_pycache"
    pycache_root.mkdir(parents=True, exist_ok=True)
    sys.pycache_prefix = str(pycache_root)
