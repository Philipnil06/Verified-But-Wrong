from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runner import BASE_DIR, RESULTS_DIR


ANALYSIS_DIR = BASE_DIR / "analysis"
REPORTS_DIR = BASE_DIR / "reports"
LLM_RUNS_DIR = BASE_DIR / "llm_runs"
EXTERNAL_CASES_DIR = BASE_DIR / "external_cases"
DOCS_DIR = BASE_DIR / "docs"
PROMPTS_DIR = BASE_DIR / "prompts"


PRIMARY_CAUSAL_POLICY_CARD = {
    "refund_double_refund": "payments.refund.no_double_refund",
    "access_control_delete_user": "access.destructive.admin_only",
    "discount_nonnegative_price": "pricing.final_price_non_negative",
    "rate_limiter_boundary": "rate.limit.sixth_blocked",
    "expiry_handle_today": "inventory.expiry.lead_time",
    "payment_webhook_idempotency": "payments.webhook.idempotent_event",
    "refund_window_expiry": "payments.refund.window_30_days",
    "loyalty_refund_reversal": "payments.refund.reverse_dependent_rewards",
    "tenant_isolation_export": "tenant.export.isolation",
    "role_downgrade_session_invalidation": "access.role_downgrade.invalidate_sessions",
    "audit_log_retention_delete_user": "audit.delete.preserve_records",
    "invoice_cancellation_stock_restore": "invoice.cancel.restore_stock",
}


def ensure_analysis_dirs() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    LLM_RUNS_DIR.mkdir(parents=True, exist_ok=True)
    EXTERNAL_CASES_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    ensure_analysis_dirs()
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_markdown(path: Path, text: str) -> None:
    ensure_analysis_dirs()
    path.write_text(text, encoding="utf-8")


def load_evaluation_manifest() -> dict[str, Any]:
    return load_json(BASE_DIR / "evaluation_manifest.json")


def split_for_task(task_id: str) -> str:
    manifest = load_evaluation_manifest()
    if task_id in manifest.get("development_tasks", []):
        return "development"
    if task_id in manifest.get("heldout_tasks", []):
        return "heldout"
    return "unknown"


def result_path(name: str) -> Path:
    return RESULTS_DIR / name
