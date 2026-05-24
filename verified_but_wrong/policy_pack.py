from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from runner import BASE_DIR


POLICY_PACKS_DIR = BASE_DIR / "policy_packs"

DEFAULT_TASK_POLICY_PACKS = {
    "refund_double_refund": ["generic_critical_requirements", "payments_policy"],
    "payment_webhook_idempotency": ["generic_critical_requirements", "payments_policy"],
    "refund_window_expiry": ["generic_critical_requirements", "payments_policy", "business_logic_policy"],
    "loyalty_refund_reversal": ["generic_critical_requirements", "payments_policy", "business_logic_policy"],
    "tenant_isolation_export": ["generic_critical_requirements", "multi_tenant_policy", "access_control_policy"],
    "role_downgrade_session_invalidation": ["generic_critical_requirements", "access_control_policy"],
    "audit_log_retention_delete_user": ["generic_critical_requirements", "access_control_policy", "audit_logging_policy"],
    "invoice_cancellation_stock_restore": ["generic_critical_requirements", "business_logic_policy", "inventory_policy"],
    "access_control_delete_user": ["generic_critical_requirements", "access_control_policy"],
    "discount_nonnegative_price": ["generic_critical_requirements", "business_logic_policy"],
    "rate_limiter_boundary": ["generic_critical_requirements", "multi_tenant_policy"],
    "expiry_handle_today": ["generic_critical_requirements", "inventory_policy"],
}


def _pack_path(pack_id: str) -> Path:
    name = pack_id if pack_id.endswith(".json") else f"{pack_id}.json"
    return POLICY_PACKS_DIR / name


def load_policy_pack(pack_id: str) -> dict[str, Any]:
    path = _pack_path(pack_id)
    if not path.exists():
        raise FileNotFoundError(f"Unknown policy pack: {pack_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def default_policy_pack_ids(task_id: str) -> list[str]:
    return DEFAULT_TASK_POLICY_PACKS.get(task_id, ["generic_critical_requirements"])


def load_policy_cards(task_id: str, policy_pack_ids: list[str] | None = None) -> list[dict[str, Any]]:
    pack_ids = policy_pack_ids or default_policy_pack_ids(task_id)
    cards = []
    seen_ids = set()
    for pack_id in pack_ids:
        pack = load_policy_pack(pack_id)
        for card in pack.get("policy_cards", []):
            applies = card.get("applies_to_tasks", [])
            if task_id not in applies and "*" not in applies:
                continue
            if card["id"] in seen_ids:
                continue
            card = {**card, "policy_pack_id": pack.get("id", pack_id)}
            cards.append(card)
            seen_ids.add(card["id"])
    return cards
