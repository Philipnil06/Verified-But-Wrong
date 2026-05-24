from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from analysis.common import LLM_RUNS_DIR, PRIMARY_CAUSAL_POLICY_CARD, PROMPTS_DIR, REPORTS_DIR, timestamp, write_json, write_markdown
from llm_selection import BASELINE_REQUIREMENTS, evaluate_candidates_with_requirement_tests, run_candidate_ranking_with_requirement_tests
from policy_pack import default_policy_pack_ids, load_policy_cards
from runner import BASE_DIR, list_tasks, load_task
from spec_audit_gate import STOPWORDS, audit_public_spec
from spec_repair import repair_spec_from_audit


LLM_POLICY_SPLIT_JSON = REPORTS_DIR / "llm_policy_split_eval.json"
LLM_POLICY_SPLIT_MD = REPORTS_DIR / "llm_policy_split_eval.md"
LLM_POLICY_SPLIT_EXAMPLES_MD = REPORTS_DIR / "llm_policy_split_examples.md"
PAPER_INSERT_MD = REPORTS_DIR / "paper_insert_llm_policy_split.md"
CONDITIONS = ["ticket_only", "ticket_plus_generic_checklist", "ticket_plus_retrieved_policy", "oracle_full"]
RESPONSE_SCHEMA = {
    "title": "",
    "behavior_requirements": [],
    "edge_cases": [],
    "acceptance_criteria": [],
    "non_goals": [],
    "testable_assertions": [],
}
SYSTEM_INSTRUCTION = (
    "You write implementation specifications for secure program synthesis. "
    "Be concrete, testable, and concise. Do not invent organization-specific policies "
    "unless they are implied by the provided context."
)
GENERIC_CHECKLIST = [
    "authorization and access control",
    "idempotency and duplicate handling",
    "boundary conditions and off-by-one cases",
    "state consistency and required state updates",
    "audit logging or record retention where relevant",
    "tenant or data isolation where relevant",
]


class ProviderNotConfigured(RuntimeError):
    pass


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _prompt_template(condition: str) -> str:
    file_map = {
        "ticket_only": "llm_spec_writer_ticket_only.txt",
        "ticket_plus_generic_checklist": "llm_spec_writer_generic_checklist.txt",
        "ticket_plus_retrieved_policy": "llm_spec_writer_retrieved_policy.txt",
        "oracle_full": "llm_spec_writer_oracle_full.txt",
    }
    return (PROMPTS_DIR / file_map[condition]).read_text(encoding="utf-8").strip()


def _ticket_fixture(task_id: str) -> tuple[str | None, dict[str, Any] | None]:
    naturalistic_dir = BASE_DIR / "naturalistic_specs"
    for provenance_path in naturalistic_dir.glob("*/provenance.json"):
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        if provenance.get("task_id") != task_id:
            continue
        ticket_path = provenance_path.parent / "public_ticket.md"
        if ticket_path.exists():
            return ticket_path.read_text(encoding="utf-8").strip(), provenance
    return None, None


def _ticket_text(task: dict[str, Any]) -> str:
    ticket_text, _ = _ticket_fixture(task["id"])
    if ticket_text:
        return ticket_text
    return str(task.get("visible_intent") or task.get("intent") or task.get("title"))


def _causal_policy_card(task_id: str) -> dict[str, Any] | None:
    causal_id = PRIMARY_CAUSAL_POLICY_CARD.get(task_id)
    if not causal_id:
        return None
    for card in load_policy_cards(task_id, default_policy_pack_ids(task_id)):
        if card.get("id") == causal_id:
            return card
    return None


def _retrieved_policy_text(task_id: str) -> str:
    card = _causal_policy_card(task_id)
    if not card:
        return "No task-specific policy card found."
    lines = [
        f"Policy card ID: {card['id']}",
        f"Title: {card.get('title', '')}",
        f"Requirement: {card.get('requirement', '')}",
    ]
    if card.get("why_it_matters"):
        lines.append(f"Why it matters: {card['why_it_matters']}")
    if card.get("audit_questions"):
        lines.append("Audit questions:")
        lines.extend(f"- {question}" for question in card["audit_questions"])
    if card.get("keywords"):
        lines.append("Keywords:")
        lines.extend(f"- {keyword}" for keyword in card["keywords"])
    return "\n".join(lines)


def _oracle_text(task: dict[str, Any]) -> str:
    return str(task.get("full_oracle_spec") or task.get("critic_improved_spec") or task.get("intent") or "")


def _response_format_instructions() -> str:
    return (
        "Return JSON only with this exact top-level shape:\n"
        "{\n"
        '  "title": "short title",\n'
        '  "behavior_requirements": ["..."],\n'
        '  "edge_cases": ["..."],\n'
        '  "acceptance_criteria": ["..."],\n'
        '  "non_goals": ["..."],\n'
        '  "testable_assertions": ["..."]\n'
        "}\n"
        "Do not output code."
    )


def _compose_prompt(task: dict[str, Any], condition: str) -> str:
    template = _prompt_template(condition)
    if condition == "ticket_only":
        condition_text = (
            "Use only the product ticket below. Do not assume access to hidden organization policies. "
            "Write the best implementation spec you can from the ticket."
        )
        body = f"Product ticket:\n{_ticket_text(task)}"
    elif condition == "ticket_plus_generic_checklist":
        checklist = "\n".join(f"- {item}" for item in GENERIC_CHECKLIST)
        condition_text = (
            "Use the product ticket and the generic checklist. "
            "The checklist is generic and may not mention task-specific organization policies."
        )
        body = f"Product ticket:\n{_ticket_text(task)}\n\nGeneric checklist:\n{checklist}"
    elif condition == "ticket_plus_retrieved_policy":
        condition_text = (
            "Use the product ticket and the retrieved policy card. "
            "The policy card is authoritative and must be preserved in the implementation spec if applicable."
        )
        body = f"Product ticket:\n{_ticket_text(task)}\n\nRetrieved policy card:\n{_retrieved_policy_text(task['id'])}"
    elif condition == "oracle_full":
        condition_text = "Use the full intended behavior. This is an upper-bound condition."
        body = f"Full intended behavior:\n{_oracle_text(task)}"
    else:
        raise ValueError(condition)
    return (
        f"{template}\n\n"
        f"System instruction:\n{SYSTEM_INSTRUCTION}\n\n"
        f"Condition-specific instruction:\n{condition_text}\n\n"
        f"Task title: {task['title']}\n"
        f"Function entrypoint: {task['entrypoint']}\n\n"
        f"{body}\n\n"
        f"{_response_format_instructions()}"
    )


def _cache_path(model: str, condition: str, task_id: str, run_id: int) -> Path:
    return LLM_RUNS_DIR / "specs" / model / condition / task_id / f"{run_id}.json"


def _discover_cached_models() -> list[str]:
    root = LLM_RUNS_DIR / "specs"
    if not root.exists():
        return []
    return sorted(path.name for path in root.iterdir() if path.is_dir())


def _resolve_run_count(args: argparse.Namespace) -> int:
    if args.runs is not None:
        return args.runs
    if args.smoke:
        return 1
    if args.full:
        return 5
    return 3


def _json_extract(text: str) -> dict[str, Any]:
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        data = json.loads(text[start : end + 1])
        if isinstance(data, dict):
            return data
    raise json.JSONDecodeError("No JSON object found", text, 0)


def _normalize_spec_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = {}
    for key, default in RESPONSE_SCHEMA.items():
        value = payload.get(key, default)
        if isinstance(default, list):
            if isinstance(value, str):
                items = [line.strip("- ").strip() for line in value.splitlines() if line.strip()]
            elif isinstance(value, list):
                items = [str(item).strip() for item in value if str(item).strip()]
            else:
                items = []
            normalized[key] = items
        else:
            normalized[key] = str(value or "").strip()
    return normalized


def _spec_to_text(spec: dict[str, Any]) -> str:
    lines = [f"Title: {spec['title']}"]
    sections = [
        ("Behavior requirements", spec["behavior_requirements"]),
        ("Edge cases", spec["edge_cases"]),
        ("Acceptance criteria", spec["acceptance_criteria"]),
        ("Non-goals", spec["non_goals"]),
        ("Testable assertions", spec["testable_assertions"]),
    ]
    for heading, values in sections:
        lines.append(f"\n{heading}:")
        if values:
            lines.extend(f"- {value}" for value in values)
        else:
            lines.append("- None stated.")
    return "\n".join(lines).strip()


def _parse_response_text(response_text: str) -> tuple[dict[str, Any], str]:
    if not response_text.strip():
        return _normalize_spec_payload({}), "empty_response"
    try:
        payload = _json_extract(response_text)
        return _normalize_spec_payload(payload), "json_ok"
    except Exception:
        fallback = {
            "title": "Unparsed generated specification",
            "behavior_requirements": [response_text.strip()],
            "edge_cases": [],
            "acceptance_criteria": [],
            "non_goals": [],
            "testable_assertions": [],
        }
        return _normalize_spec_payload(fallback), "raw_text_fallback"


def _load_openai_client(base_url: str | None, api_key: str):
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ProviderNotConfigured("openai package is not installed") from exc
    kwargs: dict[str, Any] = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def _openai_message_text(message: Any) -> str:
    content = getattr(message, "content", None)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            text = getattr(item, "text", None)
            if isinstance(text, str):
                parts.append(text)
            elif isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return "\n".join(parts)
    return ""


def _call_openai_compatible(model: str, prompt: str) -> tuple[str, dict[str, Any]]:
    api_key = os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ProviderNotConfigured("No OpenAI-compatible API key configured.")
    base_url = os.environ.get("LLM_BASE_URL")
    client = _load_openai_client(base_url=base_url, api_key=api_key)
    last_error = None

    if model.startswith("gpt-5"):
        response_attempts = [
            {
                "model": model,
                "instructions": SYSTEM_INSTRUCTION,
                "input": prompt,
                "max_output_tokens": 1800,
                "reasoning": {"effort": "minimal"},
                "text": {"format": {"type": "json_object"}, "verbosity": "low"},
            },
            {
                "model": model,
                "instructions": SYSTEM_INSTRUCTION,
                "input": prompt,
                "max_output_tokens": 1800,
            },
        ]
        for kwargs in response_attempts:
            try:
                response = client.responses.create(**kwargs)
                response_text = getattr(response, "output_text", None) or ""
                if not response_text:
                    output = getattr(response, "output", None) or []
                    parts = []
                    for item in output:
                        for content_item in getattr(item, "content", None) or []:
                            text = getattr(content_item, "text", None)
                            if isinstance(text, str):
                                parts.append(text)
                    response_text = "\n".join(parts)
                metadata = {
                    "provider": "openai_compatible",
                    "response_id": getattr(response, "id", None),
                    "status": getattr(response, "status", None),
                    "usage": getattr(response, "usage", None).model_dump() if getattr(response, "usage", None) else None,
                }
                return response_text, metadata
            except Exception as exc:
                last_error = exc

    messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTION},
        {"role": "user", "content": prompt},
    ]
    attempts = [
        {"model": model, "messages": messages, "response_format": {"type": "json_object"}, "max_completion_tokens": 1800},
        {"model": model, "messages": messages, "max_completion_tokens": 1800},
        {"model": model, "messages": messages, "response_format": {"type": "json_object"}},
        {"model": model, "messages": messages},
    ]
    for kwargs in attempts:
        try:
            completion = client.chat.completions.create(**kwargs)
            choice = completion.choices[0]
            response_text = _openai_message_text(choice.message)
            metadata = {
                "provider": "openai_compatible",
                "response_id": getattr(completion, "id", None),
                "finish_reason": getattr(choice, "finish_reason", None),
                "usage": getattr(completion, "usage", None).model_dump() if getattr(completion, "usage", None) else None,
            }
            return response_text, metadata
        except Exception as exc:
            last_error = exc
    raise RuntimeError(f"OpenAI-compatible request failed: {last_error}")


def _call_anthropic(model: str, prompt: str) -> tuple[str, dict[str, Any]]:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ProviderNotConfigured("No Anthropic API key configured.")
    try:
        from anthropic import Anthropic
    except ImportError as exc:
        raise ProviderNotConfigured("anthropic package is not installed") from exc
    client = Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        system=SYSTEM_INSTRUCTION,
        max_tokens=1800,
        messages=[{"role": "user", "content": prompt}],
    )
    parts = []
    for item in message.content:
        text = getattr(item, "text", None)
        if isinstance(text, str):
            parts.append(text)
    response_text = "\n".join(parts)
    metadata = {
        "provider": "anthropic",
        "response_id": getattr(message, "id", None),
        "stop_reason": getattr(message, "stop_reason", None),
        "usage": getattr(message, "usage", None).model_dump() if getattr(message, "usage", None) else None,
    }
    return response_text, metadata


def _provider_config(model_override: str | None) -> dict[str, Any]:
    if os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY"):
        model = model_override or os.environ.get("LLM_MODEL") or os.environ.get("OPENAI_MODEL") or os.environ.get("OPENAI_SPEC_MODEL") or "gpt-5.4-nano"
        provider = "openai_compatible"
        return {
            "provider": provider,
            "model": model,
            "configured": True,
            "call": _call_openai_compatible,
        }
    if os.environ.get("ANTHROPIC_API_KEY"):
        model = model_override or os.environ.get("ANTHROPIC_MODEL") or "claude-3-5-sonnet-latest"
        return {
            "provider": "anthropic",
            "model": model,
            "configured": True,
            "call": _call_anthropic,
        }
    return {
        "provider": None,
        "model": model_override or os.environ.get("LLM_MODEL") or os.environ.get("OPENAI_MODEL") or os.environ.get("ANTHROPIC_MODEL") or "unconfigured",
        "configured": False,
        "call": None,
    }


def _task_and_run_metadata(task: dict[str, Any], condition: str, run_id: int, model: str) -> dict[str, Any]:
    prompt = _compose_prompt(task, condition)
    return {
        "timestamp": timestamp(),
        "task_id": task["id"],
        "task_title": task["title"],
        "condition": condition,
        "run_id": run_id,
        "model": model,
        "prompt": prompt,
        "prompt_hash": _sha256_text(prompt),
    }


def _generate_live(task: dict[str, Any], condition: str, run_id: int, provider: dict[str, Any]) -> dict[str, Any]:
    metadata = _task_and_run_metadata(task, condition, run_id, provider["model"])
    response_text, provider_metadata = provider["call"](provider["model"], metadata["prompt"])
    parsed_spec, parse_status = _parse_response_text(response_text)
    public_spec = _spec_to_text(parsed_spec)
    return {
        **metadata,
        "provider": provider["provider"],
        "response_text": response_text,
        "response_hash": _sha256_text(response_text),
        "provider_metadata": provider_metadata,
        "parse_status": parse_status,
        "structured_spec": parsed_spec,
        "public_spec": public_spec,
        "generation_empty": not public_spec.strip(),
        "generation_error": "empty_generated_spec" if not public_spec.strip() else None,
    }


def _load_cached(path: Path) -> dict[str, Any]:
    row = json.loads(path.read_text(encoding="utf-8"))
    row.setdefault("parse_status", "unknown")
    row.setdefault("provider", "cached")
    row.setdefault("provider_metadata", {})
    row.setdefault("response_text", "")
    if "structured_spec" not in row:
        parsed_spec, parse_status = _parse_response_text(row.get("response_text") or "")
        row["structured_spec"] = parsed_spec
        row["parse_status"] = parse_status
    if "public_spec" not in row or not row.get("public_spec"):
        row["public_spec"] = _spec_to_text(row["structured_spec"])
    if "prompt_hash" not in row:
        row["prompt_hash"] = _sha256_text(row.get("prompt", ""))
    if "response_hash" not in row:
        row["response_hash"] = _sha256_text(row.get("response_text", ""))
    row.setdefault("generation_empty", not bool(str(row.get("public_spec") or "").strip()))
    row.setdefault("generation_error", "empty_generated_spec" if row["generation_empty"] else None)
    return row


def _load_or_generate(task: dict[str, Any], condition: str, run_id: int, provider: dict[str, Any], refresh: bool) -> tuple[dict[str, Any] | None, str]:
    path = _cache_path(provider["model"], condition, task["id"], run_id)
    if path.exists() and not refresh:
        return _load_cached(path), "cache"
    if path.exists() and refresh and not provider["configured"]:
        return _load_cached(path), "cache_provider_missing"
    if not refresh:
        return None, "missing_cache"
    if not provider["configured"]:
        return None, "missing_provider"
    row = _generate_live(task, condition, run_id, provider)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2, ensure_ascii=False), encoding="utf-8")
    return row, "live"


def _is_valid_spec(row: dict[str, Any]) -> bool:
    return not row.get("generation_empty") and bool(str(row.get("public_spec") or "").strip())


def _policy_keywords(card: dict[str, Any] | None) -> list[str]:
    if not card:
        return []
    return [str(keyword).lower() for keyword in card.get("keywords", []) if str(keyword).strip()]


def _related_terms(card: dict[str, Any] | None) -> list[str]:
    if not card:
        return []
    raw = f"{card.get('title', '')} {card.get('requirement', '')}"
    terms = []
    for term in raw.lower().replace("-", " ").replace("_", " ").split():
        if len(term) >= 5 and term not in STOPWORDS and term not in terms:
            terms.append(term)
    return terms


def _causal_policy_measurement(task_id: str, spec_text: str, gate: dict[str, Any]) -> dict[str, Any]:
    card = _causal_policy_card(task_id)
    text = spec_text.lower()
    exact_matches = [keyword for keyword in _policy_keywords(card) if keyword in text]
    related_matches = [term for term in _related_terms(card) if term in text]
    gate_status = "missing"
    for item in gate.get("policy_cards_checked", []):
        if card and item.get("policy_card_id") == card.get("id"):
            gate_status = item.get("status", "missing")
            break
    exact_bool = bool(exact_matches)
    related_bool = bool(related_matches)
    gate_bool = gate_status == "covered"
    ambiguous = len({exact_bool, related_bool, gate_bool}) > 1 or gate_status == "unclear"
    if gate_bool or exact_bool:
        mention_label = "mentioned" if not ambiguous else "ambiguous_policy_mention"
    elif related_bool or gate_status == "unclear":
        mention_label = "ambiguous_policy_mention"
    else:
        mention_label = "omitted"
    return {
        "causal_policy_id": card.get("id") if card else None,
        "exact_keyword_matches": exact_matches,
        "related_term_matches": related_matches,
        "gate_status": gate_status,
        "exact_keyword_covered": exact_bool,
        "related_term_covered": related_bool,
        "gate_classified_covered": gate_bool,
        "ambiguous_policy_mention": ambiguous,
        "mention_label": mention_label,
    }


def _selected_requirements_from_audit(task_id: str, audit: dict[str, Any]) -> list[str]:
    requirements = []
    baseline = BASELINE_REQUIREMENTS.get(task_id, {}).get("requirement")
    if baseline:
        requirements.append(baseline)
    for card in audit.get("covered_policy_cards", []):
        requirement_test = card.get("requirement_test")
        if requirement_test and requirement_test not in requirements:
            requirements.append(requirement_test)
    return requirements


def _public_passing_metrics(candidate_results: list[dict[str, Any]]) -> dict[str, Any]:
    public_passing = [candidate for candidate in candidate_results if candidate["public_passed"]]
    hidden_failing = [candidate for candidate in public_passing if not candidate["hidden_passed"]]
    return {
        "public_passing_candidates_count": len(public_passing),
        "public_passing_hidden_failing_count": len(hidden_failing),
        "underconstraint_risk": len(hidden_failing) / len(public_passing) if public_passing else 0.0,
    }


def _repair_result(task_id: str, public_spec: str, gate: dict[str, Any]) -> dict[str, Any]:
    needs_repair = bool(gate.get("missing_policy_cards") or gate.get("unclear_policy_cards"))
    if not needs_repair:
        return {
            "attempted": False,
            "patched_policy_card_ids": [],
            "patches": [],
            "cleared": True,
            "repaired_spec_text": public_spec,
            "gate_after": gate,
            "selection_after": None,
            "underconstraint_after": None,
        }
    repair = repair_spec_from_audit(public_spec, gate)
    gate_after = audit_public_spec(task_id, repair["repaired_spec_text"], mode="llm_policy_split_repaired")
    requirements_after = _selected_requirements_from_audit(task_id, gate_after)
    selection_after = run_candidate_ranking_with_requirement_tests(task_id, requirements_after)
    candidate_set_after = evaluate_candidates_with_requirement_tests(task_id, requirements_after)["candidate_results"]
    underconstraint_after = _public_passing_metrics(candidate_set_after)
    return {
        "attempted": True,
        "patched_policy_card_ids": repair["patched_policy_card_ids"],
        "patches": repair["patches"],
        "cleared": gate_after["pre_selection_decision"] == "ALLOW" and not selection_after["verified_but_wrong"],
        "repaired_spec_text": repair["repaired_spec_text"],
        "gate_after": {
            "pre_selection_decision": gate_after["pre_selection_decision"],
            "missing_policy_ids": [item["policy_card_id"] for item in gate_after["missing_policy_cards"]],
            "unclear_policy_ids": [item["policy_card_id"] for item in gate_after["unclear_policy_cards"]],
        },
        "selection_after": {
            "selected_candidate": selection_after["selected_candidate"],
            "verified_but_wrong": selection_after["verified_but_wrong"],
            "hidden_oracle_passed": selection_after["hidden_oracle_passed"],
        },
        "underconstraint_after": underconstraint_after,
    }


def _enrich_row(task: dict[str, Any], row: dict[str, Any], source: str) -> dict[str, Any]:
    public_spec = row.get("public_spec") or ""
    gate = audit_public_spec(task["id"], public_spec, policy_pack_ids=task.get("policy_pack_ids"), mode="llm_policy_split")
    policy_measurement = _causal_policy_measurement(task["id"], public_spec, gate)
    selected_requirements = _selected_requirements_from_audit(task["id"], gate)
    selection = run_candidate_ranking_with_requirement_tests(task["id"], selected_requirements)
    candidate_set = evaluate_candidates_with_requirement_tests(task["id"], selected_requirements)["candidate_results"]
    underconstraint = _public_passing_metrics(candidate_set)
    repair = _repair_result(task["id"], public_spec, gate)
    structured_spec = row.get("structured_spec") or _normalize_spec_payload({})
    return {
        **row,
        "source": source,
        "task_split": task.get("evaluation_split"),
        "spec_length_chars": len(public_spec),
        "spec_length_words": len(public_spec.split()),
        "structured_spec": structured_spec,
        "gate": {
            "pre_selection_decision": gate["pre_selection_decision"],
            "missing_policy_ids": [item["policy_card_id"] for item in gate["missing_policy_cards"]],
            "unclear_policy_ids": [item["policy_card_id"] for item in gate["unclear_policy_cards"]],
            "covered_policy_ids": [item["policy_card_id"] for item in gate["covered_policy_cards"]],
        },
        "policy_measurement": policy_measurement,
        "selected_requirements": selected_requirements,
        "selection": {
            "selected_candidate": selection["selected_candidate"],
            "verified_but_wrong": selection["verified_but_wrong"],
            "hidden_oracle_passed": selection["hidden_oracle_passed"],
        },
        "candidate_set_underconstraint": underconstraint,
        "repair": repair,
    }


def _condition_summary(rows: list[dict[str, Any]], condition: str, runs_per_task: int, task_count: int) -> dict[str, Any]:
    condition_rows = [row for row in rows if row["condition"] == condition]
    valid = [row for row in condition_rows if _is_valid_spec(row)]
    omitted = [row for row in valid if row["policy_measurement"]["mention_label"] == "omitted"]
    ambiguous = [row for row in valid if row["policy_measurement"]["mention_label"] == "ambiguous_policy_mention"]
    dangerous = [row for row in valid if row["selection"]["verified_but_wrong"]]
    gate_caught = [row for row in dangerous if row["gate"]["pre_selection_decision"] in {"REVIEW", "BLOCK"}]
    gate_allowed = [row for row in dangerous if row["gate"]["pre_selection_decision"] == "ALLOW"]
    repair_attempted = [row for row in valid if row["repair"]["attempted"]]
    repair_cleared = [row for row in repair_attempted if row["repair"]["cleared"]]
    return {
        "condition": condition,
        "total_requested_runs": task_count * runs_per_task,
        "valid_specs": len(valid),
        "invalid_specs": len(condition_rows) - len(valid),
        "parse_failures": sum(1 for row in condition_rows if row.get("parse_status") != "json_ok"),
        "causal_policy_mentioned_count": sum(1 for row in valid if row["policy_measurement"]["mention_label"] == "mentioned"),
        "causal_policy_omitted_count": len(omitted),
        "causal_policy_omission_rate": len(omitted) / len(valid) if valid else 0.0,
        "ambiguous_policy_mention_count": len(ambiguous),
        "selected_vbw_count": len(dangerous),
        "selected_vbw_rate": len(dangerous) / len(valid) if valid else 0.0,
        "gate_allowed_dangerous_count": len(gate_allowed),
        "gate_caught_dangerous_count": len(gate_caught),
        "repair_attempted_count": len(repair_attempted),
        "repair_cleared_count": len(repair_cleared),
        "mean_spec_length_chars": sum(row["spec_length_chars"] for row in valid) / len(valid) if valid else 0.0,
        "mean_spec_length_words": sum(row["spec_length_words"] for row in valid) / len(valid) if valid else 0.0,
        "mean_underconstraint_risk": (
            sum(row["candidate_set_underconstraint"]["underconstraint_risk"] for row in valid) / len(valid) if valid else None
        ),
        "tasks_with_any_vbw": len({row["task_id"] for row in dangerous}),
        "tasks_with_any_policy_omission": len({row["task_id"] for row in omitted}),
    }


def _task_condition_rows(rows: list[dict[str, Any]], condition: str, task_id: str) -> list[dict[str, Any]]:
    return [row for row in rows if row["condition"] == condition and row["task_id"] == task_id]


def _task_condition_summary(rows: list[dict[str, Any]], condition: str, task_id: str) -> dict[str, Any]:
    task_rows = _task_condition_rows(rows, condition, task_id)
    valid = [row for row in task_rows if _is_valid_spec(row)]
    examples = []
    for row in task_rows[:2]:
        examples.append(
            {
                "run_id": row["run_id"],
                "mention_label": row["policy_measurement"]["mention_label"],
                "gate_decision": row["gate"]["pre_selection_decision"],
                "selected_candidate": row["selection"]["selected_candidate"],
                "selected_vbw": row["selection"]["verified_but_wrong"],
                "repair_cleared": row["repair"]["cleared"],
            }
        )
    return {
        "task_id": task_id,
        "condition": condition,
        "valid_specs": len(valid),
        "causal_policy_omitted": sum(1 for row in valid if row["policy_measurement"]["mention_label"] == "omitted"),
        "selected_vbw": sum(1 for row in valid if row["selection"]["verified_but_wrong"]),
        "gate_decisions": dict(Counter(row["gate"]["pre_selection_decision"] for row in valid)),
        "repair_cleared": sum(1 for row in valid if row["repair"]["cleared"]),
        "examples": examples,
    }


def _status_for_run(rows: list[dict[str, Any]], provider: dict[str, Any], missing_cache: bool, live_calls: int, requested_runs: int) -> str:
    completed_runs = len(rows)
    if live_calls > 0 and completed_runs == requested_runs:
        return "passed"
    if completed_runs > 0 and completed_runs < requested_runs:
        return "partial_cached_coverage" if live_calls == 0 else "partial_live_coverage"
    if rows:
        return "passed"
    if not provider["configured"] and missing_cache:
        return "not_run_no_provider_config"
    if missing_cache:
        return "not_run_no_cached_specs"
    return "passed"


def _pick_example_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    priority = sorted(
        rows,
        key=lambda row: (
            0 if row["policy_measurement"]["mention_label"] == "omitted" else 1,
            0 if row["selection"]["verified_but_wrong"] else 1,
            0 if row["repair"]["attempted"] else 1,
            row["condition"],
            row["task_id"],
            row["run_id"],
        ),
    )
    picked = []
    seen = set()
    for row in priority:
        key = (row["condition"], row["task_id"])
        if key in seen:
            continue
        picked.append(row)
        seen.add(key)
        if len(picked) == 5:
            break
    return picked[:5]


def _main_table_lines(summaries: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Condition | Valid specs | Causal policy omitted | Selected VBW | Gate caught dangerous | Repair cleared |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in summaries:
        lines.append(
            f"| `{row['condition']}` | {row['valid_specs']} | {row['causal_policy_omitted_count']} | "
            f"{row['selected_vbw_count']} | {row['gate_caught_dangerous_count']} | {row['repair_cleared_count']} |"
        )
    return lines


def _write_markdown_reports(result: dict[str, Any]) -> None:
    lines = [
        "# LLM Policy-Split Evaluation",
        "",
        f"- status: `{result['status']}`",
        f"- live API calls run: `{result['live_api_calls_run']}`",
        f"- cache hits used: `{result['cache_hits_used']}`",
        f"- model: `{result['model']}`",
        f"- provider: `{result['provider']}`",
        f"- requested runs: `{result['requested_runs']}`",
        f"- completed runs: `{result['completed_runs']}`",
        f"- valid specs: `{sum(row['valid_specs'] for row in result['summaries'])}`",
        "",
    ]
    if result.get("message"):
        lines.extend([result["message"], ""])
    lines.extend(_main_table_lines(result["summaries"]))
    lines.extend(
        [
            "",
            "## Per-Task Table",
            "",
            "| Task | Condition | Valid specs | Causal policy omitted | Selected VBW | Gate decisions | Repair cleared |",
            "|---|---|---:|---:|---:|---|---:|",
        ]
    )
    for row in result["per_task_condition"]:
        gate_decisions = ", ".join(f"{key}:{value}" for key, value in sorted(row["gate_decisions"].items())) or "-"
        lines.append(
            f"| `{row['task_id']}` | `{row['condition']}` | {row['valid_specs']} | {row['causal_policy_omitted']} | "
            f"{row['selected_vbw']} | {gate_decisions} | {row['repair_cleared']} |"
        )
    lines.extend(["", "## Cautious Interpretation", ""])
    if sum(row["valid_specs"] for row in result["summaries"]) == 0:
        lines.append(
            "No generated specs were available. This remains infrastructure and reproduction scaffolding, not quantitative LLM evidence."
        )
    else:
        lines.append(result["interpretation"])
    lines.extend(["", "## Limitations", ""])
    for item in result["limitations"]:
        lines.append(f"- {item}")
    write_markdown(LLM_POLICY_SPLIT_MD, "\n".join(lines))

    example_lines = ["# LLM Policy-Split Examples", ""]
    if not result["example_rows"]:
        example_lines.append("No generated spec artifacts were available.")
    for row in result["example_rows"]:
        example_lines.extend(
            [
                f"## {row['condition']} / {row['task_id']} / run {row['run_id']}",
                "",
                "### Product ticket",
                "",
                _ticket_text(load_task(row["task_id"])),
                "",
                "### Generated spec excerpt",
                "",
                "```text",
                (row["public_spec"] or "")[:800],
                "```",
                "",
                f"- causal policy card: `{row['policy_measurement']['causal_policy_id']}`",
                f"- policy mention label: `{row['policy_measurement']['mention_label']}`",
                f"- gate decision: `{row['gate']['pre_selection_decision']}`",
                f"- selected candidate result: `{row['selection']['selected_candidate']}`, VBW=`{row['selection']['verified_but_wrong']}`",
                f"- after repair result: `{row['repair']['selection_after']['selected_candidate'] if row['repair']['selection_after'] else row['selection']['selected_candidate']}`, "
                f"VBW=`{row['repair']['selection_after']['verified_but_wrong'] if row['repair']['selection_after'] else row['selection']['verified_but_wrong']}`",
                "",
            ]
        )
    write_markdown(LLM_POLICY_SPLIT_EXAMPLES_MD, "\n".join(example_lines))

    insert_lines = []
    if sum(row["valid_specs"] for row in result["summaries"]) == 0:
        insert_lines.extend(
            [
                "Earlier saved LLM pilot artifacts did not naturally produce verified-but-wrong selections on small tasks.",
                "The policy-split runner is now reproducible and cache-first, but this repository currently has no cached or live generated specs for the experiment.",
                "Do not include this section as quantitative evidence until real artifacts exist under `llm_runs/specs/`.",
            ]
        )
    else:
        insert_lines.extend(
            [
                "Earlier saved LLM pilot artifacts did not naturally produce verified-but-wrong selections on small tasks. "
                "We therefore ran a policy-split spec-writing experiment that better matches the intended deployment concern: "
                "product tickets often omit organization policies because those policies live in separate inventories.",
                "",
                *_main_table_lines(result["summaries"]),
                "",
                "One concrete example:",
            ]
        )
        if result["example_rows"]:
            example = result["example_rows"][0]
            insert_lines.extend(
                [
                    f"- task: `{example['task_id']}`",
                    f"- condition: `{example['condition']}`",
                    f"- causal policy card: `{example['policy_measurement']['causal_policy_id']}`",
                    f"- policy mention label: `{example['policy_measurement']['mention_label']}`",
                    f"- gate decision: `{example['gate']['pre_selection_decision']}`",
                    f"- selected candidate before repair: `{example['selection']['selected_candidate']}`",
                    f"- selected candidate after repair: `{example['repair']['selection_after']['selected_candidate'] if example['repair']['selection_after'] else example['selection']['selected_candidate']}`",
                    "",
                    result["interpretation"],
                    "",
                    "Limitations: this result depends on a small controlled benchmark, rule-based policy mention scoring, and cached API artifacts rather than fresh end-to-end reruns in every reproduction.",
                ]
            )
    write_markdown(PAPER_INSERT_MD, "\n".join(insert_lines))


def run_llm_policy_split_eval(runs_per_task: int = 3, model: str | None = None, refresh: bool = False) -> dict[str, Any]:
    provider = _provider_config(model)
    tasks = list_tasks()
    rows = []
    missing_cache = False
    live_calls = 0
    cache_hits = 0
    models_to_use = [provider["model"]]
    if not refresh and model is None:
        cached_models = _discover_cached_models()
        if cached_models:
            models_to_use = cached_models
    for model_name in models_to_use:
        active_provider = {**provider, "model": model_name}
        for task in tasks:
            for condition in CONDITIONS:
                for run_id in range(1, runs_per_task + 1):
                    loaded, source = _load_or_generate(task, condition, run_id, active_provider, refresh=refresh)
                    if loaded is None:
                        missing_cache = True
                        continue
                    if source == "live":
                        live_calls += 1
                    else:
                        cache_hits += 1
                    rows.append(_enrich_row(task, loaded, source))

    requested_runs = len(tasks) * len(CONDITIONS) * runs_per_task
    status = _status_for_run(rows, provider, missing_cache, live_calls, requested_runs)
    summaries = [_condition_summary(rows, condition, runs_per_task, len(tasks)) for condition in CONDITIONS]
    per_task_condition = []
    for condition in CONDITIONS:
        for task in tasks:
            per_task_condition.append(_task_condition_summary(rows, condition, task["id"]))
    if sum(row["valid_specs"] for row in summaries) == 0:
        interpretation = "No generated specs were available, so there is no quantitative evidence yet about policy omission under the split conditions."
    else:
        omission = {row["condition"]: row["causal_policy_omission_rate"] for row in summaries}
        if omission.get("ticket_only", 0.0) > omission.get("ticket_plus_retrieved_policy", 0.0):
            interpretation = (
                "Ticket-only and generic-checklist specs omit known policies more often than specs given retrieved policy cards. "
                "This supports the target-validity framing: product tickets alone should not be trusted to preserve organization-level requirements."
            )
        else:
            interpretation = (
                "These runs do not show a stronger omission rate for ticket-only specs than for retrieved-policy specs. "
                "That weakens the motivating claim for this particular model/task mix and should be reported directly."
            )
    message = None
    if status == "not_run_no_provider_config":
        message = (
            "No cached specs were found for the requested run set, and no provider configuration was available for live generation. "
            "Set `LLM_API_KEY`/`OPENAI_API_KEY` or `ANTHROPIC_API_KEY`, then rerun with `--refresh`."
        )
    elif status == "not_run_no_cached_specs":
        message = "No cached specs were found for the requested run set. Rerun with `--refresh` to generate live artifacts."
    result = {
        "result_type": "llm_policy_split_eval",
        "timestamp": timestamp(),
        "status": status,
        "provider": provider["provider"] or "unconfigured",
        "model": provider["model"],
        "runs_per_task": runs_per_task,
        "requested_runs": requested_runs,
        "completed_runs": len(rows),
        "conditions": CONDITIONS,
        "live_api_calls_run": live_calls,
        "cache_hits_used": cache_hits,
        "message": message,
        "rows": rows,
        "summaries": summaries,
        "per_task_condition": per_task_condition,
        "example_rows": _pick_example_rows(rows),
        "interpretation": interpretation,
        "limitations": [
            "The benchmark has 12 small controlled tasks rather than a production ticket corpus.",
            "Policy mention scoring combines exact keywords, related terms, and gate classification; disagreements are marked ambiguous rather than forced into a binary label.",
            "Candidate selection and repair rely on curated executable requirement tests and deterministic text patching.",
            "No live API call is made during `run_all_repro.py`; cached artifacts are required for paper-ready quantitative evidence in default reproduction.",
        ],
    }
    write_json(LLM_POLICY_SPLIT_JSON, result)
    _write_markdown_reports(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--runs", type=int, default=None)
    parser.add_argument("--cached", action="store_true")
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--model", default=None)
    args = parser.parse_args()

    runs = _resolve_run_count(args)
    refresh = bool(args.refresh and not args.cached)
    result = run_llm_policy_split_eval(runs_per_task=runs, model=args.model, refresh=refresh)
    print(json.dumps({"status": result["status"], "model": result["model"], "valid_specs": sum(item["valid_specs"] for item in result["summaries"])}, indent=2))


if __name__ == "__main__":
    main()
