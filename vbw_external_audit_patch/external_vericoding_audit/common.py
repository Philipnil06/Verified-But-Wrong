#!/usr/bin/env python3
"""Shared helpers for the External Vericoding Benchmark Audit.

The helpers are intentionally conservative: they normalize multiple public
benchmark schemas, write skipped reports instead of crashing reproduction when
network/data are unavailable, and never treat scanner output as validation.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
CASES = ROOT / "external_vericoding_cases"
EXTERNAL_DATA = ROOT / "external_data"


@dataclass(frozen=True)
class DatasetVariant:
    key: str
    repo_name: str
    repo_url: str
    local_root: Path
    jsonl_rel: Path
    raw_url: str

    @property
    def jsonl_path(self) -> Path:
        return self.local_root / self.jsonl_rel


DATASET_VARIANTS: List[DatasetVariant] = [
    DatasetVariant(
        key="benchmark",
        repo_name="vericoding-benchmark",
        repo_url="https://github.com/Beneficial-AI-Foundation/vericoding-benchmark",
        local_root=EXTERNAL_DATA / "vericoding-benchmark",
        jsonl_rel=Path("jsonl/dafny_tasks.jsonl"),
        raw_url="https://raw.githubusercontent.com/Beneficial-AI-Foundation/vericoding-benchmark/main/jsonl/dafny_tasks.jsonl",
    ),
    DatasetVariant(
        key="tools",
        repo_name="vericoding",
        repo_url="https://github.com/Beneficial-AI-Foundation/vericoding",
        local_root=EXTERNAL_DATA / "vericoding",
        jsonl_rel=Path("benchmarks/dafny_tasks.jsonl"),
        raw_url="https://raw.githubusercontent.com/Beneficial-AI-Foundation/vericoding/main/benchmarks/dafny_tasks.jsonl",
    ),
]

FIELD_ALIASES: Dict[str, Tuple[str, ...]] = {
    "task_id": ("id", "task-id", "task_id", "vc-id", "vc_id", "source-id", "source_id"),
    "language": ("language", "lang"),
    "source": ("source", "benchmark", "dataset"),
    "source_id": ("source-id", "source_id", "original_id", "original-id"),
    "description": ("vc-description", "description", "nl-description", "nl_description", "problem_statement", "problem-statement", "docstring"),
    "preamble": ("vc-preamble", "vc_preamble", "preamble"),
    "helpers": ("vc-helpers", "vc_helpers", "helpers"),
    "spec": ("vc-spec", "vc_spec", "spec"),
    "code": ("vc-code", "vc_code", "code"),
    "postamble": ("vc-postamble", "vc_postamble", "postamble"),
    "qa_score": ("qa-score", "qa_score", "quality_score"),
}

GENERIC_DESCRIPTION_PATTERNS = [
    r"^\s*process\s+input\s*\.?\s*$",
    r"^\s*sort\s+elements\s*\.?\s*$",
    r"^\s*ensures\s*:\s*returns?\s+the\s+correct\s+value\s*\.?\s*$",
    r"^\s*the\s+condition\s+holds\s+for\s+all\s+values\s*\.?\s*$",
    r"^\s*return\s+the\s+correct\s+answer\s*\.?\s*$",
    r"^\s*write\s+a\s+function\s*\.?\s*$",
]

SOURCE_BUCKETS = {"apps", "humaneval", "dafnybench", "bignum"}


def ensure_dirs() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    CASES.mkdir(parents=True, exist_ok=True)
    EXTERNAL_DATA.mkdir(parents=True, exist_ok=True)


def backup_path(path: Path) -> Path:
    i = 1
    while True:
        candidate = path.with_name(path.name + f".bak{i}")
        if not candidate.exists():
            return candidate
        i += 1


def safe_copytree(src: Path, dst: Path, refresh: bool = False) -> None:
    if dst.exists():
        if refresh:
            shutil.rmtree(dst)
        else:
            raise FileExistsError(f"Refusing to overwrite existing directory without --refresh: {dst}")
    shutil.copytree(src, dst)


def first_present(record: Dict[str, Any], names: Iterable[str]) -> Any:
    for name in names:
        if name in record and record.get(name) not in (None, ""):
            return record.get(name)
    return None


def normalize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Return a normalized task view while preserving the raw record."""
    normalized: Dict[str, Any] = {"raw": record}
    for canonical, aliases in FIELD_ALIASES.items():
        normalized[canonical] = first_present(record, aliases)
    if not normalized.get("task_id"):
        normalized["task_id"] = normalized.get("source_id") or "unknown"
    if not normalized.get("source_id"):
        normalized["source_id"] = normalized.get("task_id")
    for key in ["task_id", "language", "source", "source_id", "description", "preamble", "helpers", "spec", "code", "postamble"]:
        normalized[key] = str(normalized.get(key) or "").strip()
    normalized["source_bucket"] = normalize_source(normalized.get("source"))
    normalized["spec_full"] = join_spec_parts(normalized)
    normalized["qa_score_float"] = quality_score(record)
    normalized["missing_canonical_fields"] = [
        k for k in ["task_id", "source", "description", "spec"] if not normalized.get(k)
    ]
    return normalized


def join_spec_parts(normalized: Dict[str, Any]) -> str:
    parts = [normalized.get("preamble", ""), normalized.get("helpers", ""), normalized.get("spec", ""), normalized.get("postamble", "")]
    return "\n".join(p for p in parts if p).strip()


def normalize_source(source: str | None) -> str:
    s = (source or "").strip().lower()
    if "apps" == s or s.endswith("/apps") or "apps" in s.split("_"):
        return "apps"
    if "humaneval" in s or "human-eval" in s:
        return "humaneval"
    if "dafnybench" in s or "dafny_bench" in s:
        return "dafnybench"
    if "bignum" in s or "big_num" in s:
        return "bignum"
    return s if s in SOURCE_BUCKETS else "other"


def description_text(record_or_norm: Dict[str, Any]) -> str:
    if "description" in record_or_norm and "raw" in record_or_norm:
        return str(record_or_norm.get("description") or "").strip()
    return str(first_present(record_or_norm, FIELD_ALIASES["description"]) or "").strip()


def spec_text(record_or_norm: Dict[str, Any]) -> str:
    if "spec_full" in record_or_norm and "raw" in record_or_norm:
        return str(record_or_norm.get("spec_full") or "").strip()
    norm = normalize_record(record_or_norm)
    return str(norm.get("spec_full") or "").strip()


def task_id(record_or_norm: Dict[str, Any]) -> str:
    if "task_id" in record_or_norm and "raw" in record_or_norm:
        return str(record_or_norm.get("task_id") or "unknown")
    return str(normalize_record(record_or_norm).get("task_id") or "unknown")


def useful_description(record_or_norm: Dict[str, Any]) -> bool:
    """Heuristic viability filter, not a factual/paper result by itself."""
    norm = record_or_norm if "raw" in record_or_norm else normalize_record(record_or_norm)
    desc = description_text(norm)
    if len(desc) < 80:
        return False
    compact = re.sub(r"\s+", " ", desc).strip().lower()
    for pat in GENERIC_DESCRIPTION_PATTERNS:
        if re.match(pat, compact, flags=re.IGNORECASE):
            return False
    semantic_keywords = [
        "given", "find", "return", "determine", "count", "minimum", "maximum",
        "array", "string", "sequence", "operations", "simulate", "game",
        "possible", "if", "when", "exactly", "sort", "k-th", "kth", "smallest",
        "largest", "number", "value", "total", "sum", "output", "input",
    ]
    has_semantic = sum(1 for k in semantic_keywords if k in compact) >= 2
    if norm.get("source_bucket") == "apps":
        return has_semantic or len(compact) >= 140
    return has_semantic and len(compact) >= 100


def quality_score(record: Dict[str, Any]) -> Optional[float]:
    val = first_present(record, FIELD_ALIASES["qa_score"])
    if val in (None, ""):
        return None
    try:
        f = float(val)
    except (TypeError, ValueError):
        return None
    # In public examples, -1 appears to mean unavailable/not applicable.
    if f < 0:
        return None
    return f


def field_frequencies(records: Iterable[Dict[str, Any]]) -> Counter:
    c: Counter = Counter()
    for rec in records:
        c.update(rec.keys())
    return c


def load_jsonl(path: Optional[Path] = None) -> List[Dict[str, Any]]:
    if path is None:
        path, _ = resolve_dafny_jsonl_path()
    if path is None or not path.exists():
        raise FileNotFoundError("No supported Dafny JSONL found. Run fetch_external_benchmark.py first or place a JSONL file manually.")
    records: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON at {path}:{lineno}: {e}") from e
            if isinstance(rec, dict):
                records.append(rec)
    return records


def resolve_dafny_jsonl_path() -> Tuple[Optional[Path], Dict[str, Any]]:
    """Return the first supported local JSONL path plus source metadata."""
    for variant in DATASET_VARIANTS:
        if variant.jsonl_path.exists():
            return variant.jsonl_path, dataset_metadata(variant, fetch_method="local")
    return None, {
        "status": "missing",
        "fetch_method": "skipped",
        "repo_name": None,
        "repo_url": None,
        "local_path": None,
        "jsonl_path": None,
        "commit_hash": None,
        "supported_paths": [str(v.jsonl_path) for v in DATASET_VARIANTS],
    }


def variant_for_key(key: str) -> DatasetVariant:
    for v in DATASET_VARIANTS:
        if v.key == key:
            return v
    raise KeyError(key)


def variants_for_repo_arg(repo: str) -> List[DatasetVariant]:
    if repo == "auto":
        return DATASET_VARIANTS
    if repo == "benchmark":
        return [variant_for_key("benchmark")]
    if repo in {"tools", "vericoding"}:
        return [variant_for_key("tools")]
    raise ValueError(f"Unsupported repo option: {repo}")


def variant_for_jsonl_path(path: Path) -> Optional[DatasetVariant]:
    rp = path.resolve()
    for variant in DATASET_VARIANTS:
        try:
            rp.relative_to(variant.local_root.resolve())
            return variant
        except ValueError:
            pass
        if rp.name == variant.jsonl_path.name and str(variant.jsonl_rel.parent).replace("\\", "/") in str(rp.parent).replace("\\", "/"):
            return variant
    return None


def resolve_external_repo_root(jsonl_path: Optional[Path] = None) -> Optional[Path]:
    if jsonl_path is None:
        jsonl_path, _ = resolve_dafny_jsonl_path()
    if jsonl_path is None:
        return None
    for variant in DATASET_VARIANTS:
        try:
            jsonl_path.resolve().relative_to(variant.local_root.resolve())
            return variant.local_root
        except ValueError:
            continue
    return jsonl_path.parent


def dataset_metadata(variant: DatasetVariant, fetch_method: str = "local", jsonl_path: Optional[Path] = None) -> Dict[str, Any]:
    jsonl = jsonl_path or variant.jsonl_path
    return {
        "status": "available" if jsonl.exists() else "missing",
        "repo_name": variant.repo_name,
        "repo_url": variant.repo_url,
        "local_path": str(variant.local_root),
        "jsonl_path": str(jsonl),
        "commit_hash": get_git_commit(variant.local_root) or "unknown",
        "fetch_method": fetch_method,
    }


def get_git_commit(repo_dir: Path) -> Optional[str]:
    if (repo_dir / ".git").exists():
        try:
            out = subprocess.check_output(["git", "-C", str(repo_dir), "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL)
            return out.strip()
        except Exception:
            return None
    marker = repo_dir / "EXTERNAL_COMMIT.txt"
    if marker.exists():
        txt = marker.read_text(encoding="utf-8").strip()
        return txt or None
    return None


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_skipped_report(reason: str, metadata: Optional[Dict[str, Any]] = None) -> None:
    ensure_dirs()
    data = {"status": "skipped", "reason": reason, "dataset": metadata or resolve_dafny_jsonl_path()[1]}
    write_json(REPORTS / "external_vericoding_skipped.json", data)
    md = [
        "# External Vericoding Audit Skipped",
        "",
        reason,
        "",
        "This skip is intentionally soft-failing: unrelated internal reproduction steps should still run.",
        "",
        "## Supported local data paths",
        "",
    ]
    for v in DATASET_VARIANTS:
        md.append(f"- `{v.jsonl_path}`")
    md += ["", "## Metadata", "", fenced_json(data)]
    write_text(REPORTS / "external_vericoding_skipped.md", "\n".join(md) + "\n")


def short_excerpt(text: str, max_chars: int = 900) -> str:
    text = re.sub(r"\s+", " ", (text or "")).strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def fenced_excerpt(text: str, max_chars: int = 1400, lang: str = "") -> str:
    body = (text or "").strip()
    if len(body) > max_chars:
        body = body[: max_chars - 3].rstrip() + "..."
    return f"```{lang}\n{body}\n```"


def fenced_json(obj: Any) -> str:
    return "```json\n" + json.dumps(obj, indent=2, ensure_ascii=False) + "\n```"


def markdown_table(headers: List[str], rows: Iterable[Iterable[Any]]) -> str:
    def cell(x: Any) -> str:
        s = "" if x is None else str(x)
        s = s.replace("\n", "<br>").replace("|", "\\|")
        return s
    headers_s = [cell(h) for h in headers]
    out = ["| " + " | ".join(headers_s) + " |", "| " + " | ".join(["---"] * len(headers_s)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(cell(c) for c in row) + " |")
    return "\n".join(out) + "\n"


def safe_case_id(raw: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(raw or "unknown"))


def source_counts(records: List[Dict[str, Any]]) -> Counter:
    return Counter(normalize_record(r).get("source_bucket") for r in records)


def spec_ensures_lines(spec: str) -> List[str]:
    return [ln.strip() for ln in (spec or "").splitlines() if re.search(r"\bensures\b", ln)]


def spec_strength_score(spec: str) -> int:
    spec_l = (spec or "").lower()
    strong = [
        "forall", "exists", "multiset", "permutation", "count", "sum", "sorted", "==>", "<==>",
        " iff ", "equivalence", "function ", "predicate ", "lemma", "old(", "decreases", "validinput",
        "correctresult", "result ==", "result <=", "result >=", "result in", "forall x", "forall i",
    ]
    return sum(1 for tok in strong if tok in spec_l)


def is_trivial_or_shape_only_spec(spec: str) -> bool:
    spec_l = re.sub(r"\s+", " ", (spec or "").strip().lower())
    ensures = spec_ensures_lines(spec)
    if not ensures:
        return True
    joined = " ".join(ensures).lower()
    trivial_patterns = [
        r"ensures\s+true\b",
        r"ensures\s+result\s*>=\s*0\b",
        r"ensures\s+0\s*<=\s*result\b",
        r"ensures\s+result\s*<=\s*[^&|=]+$",
        r"ensures\s*\|\s*result\s*\|\s*>=\s*0\b",
        r"ensures\s+validresult\s*\(\s*result",
        r"ensures\s+result\s*\.len\s*\(\s*\)\s*>=\s*0",
    ]
    if len(ensures) <= 2 and any(re.search(p, joined) for p in trivial_patterns):
        # A ValidResult helper can be strong, but in candidate ranking we treat a
        # single result-only predicate as suspicious until manually inspected.
        if not re.search(r"forall|exists|multiset|permutation|correctresult|result\s*==|<==>|==>", joined):
            return True
    if len(ensures) == 1 and "result" in joined and spec_strength_score(spec_l) <= 2:
        return True
    return False


def count_lines(text: str) -> int:
    return len([ln for ln in (text or "").splitlines() if ln.strip()])
