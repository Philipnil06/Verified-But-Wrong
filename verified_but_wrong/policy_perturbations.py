from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from policy_pack import POLICY_PACKS_DIR


def load_all_policy_cards() -> list[dict[str, Any]]:
    cards = []
    for pack_path in sorted(POLICY_PACKS_DIR.glob("*.json")):
        pack = json.loads(pack_path.read_text(encoding="utf-8"))
        for card in pack.get("policy_cards", []):
            cards.append({**card, "policy_pack_id": pack.get("id", pack_path.stem)})
    return cards


def irrelevant_policy_pool(task_id: str, relevant_cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    relevant_ids = {card["id"] for card in relevant_cards}
    pool = []
    for card in load_all_policy_cards():
        applies = set(card.get("applies_to_tasks", []))
        if card["id"] in relevant_ids:
            continue
        if task_id in applies:
            continue
        pool.append(card)
    return sorted(pool, key=lambda card: card["id"])


def add_irrelevant_noise(
    task_id: str,
    relevant_cards: list[dict[str, Any]],
    factor: int,
) -> list[dict[str, Any]]:
    if factor <= 1:
        return copy.deepcopy(relevant_cards)
    pool = irrelevant_policy_pool(task_id, relevant_cards)
    if not pool:
        return copy.deepcopy(relevant_cards)
    noisy = [copy.deepcopy(card) for card in relevant_cards]
    target_irrelevant = len(relevant_cards) * (factor - 1)
    for index in range(target_irrelevant):
        source = copy.deepcopy(pool[index % len(pool)])
        source["id"] = f"{source['id']}.noise_{index + 1}"
        source["applies_to_tasks"] = source.get("applies_to_tasks", []) + [task_id]
        source["severity"] = "low"
        source["category"] = "error_behavior_omission"
        source["title"] = f"Noisy unrelated policy: {source.get('title', '')}"
        source["requirement"] = "Unrelated policy noise for robustness evaluation."
        source["keywords"] = [f"noise_token_{index + 1}"]
        noisy.append(source)
    return noisy


def weaken_wording(card: dict[str, Any]) -> dict[str, Any]:
    weakened = copy.deepcopy(card)
    weakened["title"] = f"Generalized guidance: {card.get('title', '').lower()}"
    weakened["requirement"] = (
        "The specification should remain aligned with relevant organizational expectations "
        "for this operation."
    )
    weakened["keywords"] = [
        "organizational expectation",
        "relevant safeguard",
        "business alignment",
        "important consideration",
    ]
    return weakened


def apply_outdated_wording(cards: list[dict[str, Any]], causal_policy_id: str | None) -> list[dict[str, Any]]:
    rewritten = []
    for card in cards:
        if causal_policy_id and card["id"] == causal_policy_id:
            rewritten.append(weaken_wording(card))
        else:
            rewritten.append(copy.deepcopy(card))
    return rewritten


def remove_causal_policy(cards: list[dict[str, Any]], causal_policy_id: str | None) -> list[dict[str, Any]]:
    if not causal_policy_id:
        return [copy.deepcopy(card) for card in cards]
    return [copy.deepcopy(card) for card in cards if card["id"] != causal_policy_id]
