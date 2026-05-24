from __future__ import annotations

import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runner import BASE_DIR, RESULTS_DIR, list_tasks, load_task

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv(BASE_DIR / ".env")

DEFAULT_SPEC_MODEL = "gpt-5.4-nano"
FALLBACK_CLASSIFICATION_MODEL = "gpt-5-nano"
LLM_SPEC_RUNS_JSONL = RESULTS_DIR / "llm_spec_runs.jsonl"
LLM_SPEC_LATEST_JSON = RESULTS_DIR / "llm_spec_latest.json"
LLM_MODEL_COMPARISON_LATEST_JSON = RESULTS_DIR / "llm_model_comparison_latest.json"
DEBUG_RAW_OPENAI_RESPONSES_JSONL = RESULTS_DIR / "debug_raw_openai_responses.jsonl"


class ProviderNotConfigured(RuntimeError):
    pass


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_results_dir() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def get_openai_client():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ProviderNotConfigured("OPENAI_API_KEY not set")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ProviderNotConfigured("openai package is not installed") from exc

    return OpenAI(api_key=api_key)


def _default_model(model: str | None = None) -> str:
    return model or os.environ.get("OPENAI_SPEC_MODEL") or DEFAULT_SPEC_MODEL


def _extract_json(content: str) -> dict[str, Any]:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start >= 0 and end > start:
            return json.loads(content[start : end + 1])
        raise


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if hasattr(value, "model_dump"):
        return _json_safe(value.model_dump())
    if hasattr(value, "to_dict"):
        return _json_safe(value.to_dict())
    return repr(value)


def _response_to_dict(response: Any) -> dict[str, Any]:
    safe = _json_safe(response)
    return safe if isinstance(safe, dict) else {"value": safe}


def _extract_response_text(response_dict: dict[str, Any]) -> str:
    choices = response_dict.get("choices") or []
    if choices:
        message = choices[0].get("message") or {}
        content = message.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict):
                    text = item.get("text") or item.get("content")
                    if isinstance(text, str):
                        parts.append(text)
                elif isinstance(item, str):
                    parts.append(item)
            return "\n".join(parts)
    output = response_dict.get("output") or []
    if isinstance(output, list):
        parts = []
        for item in output:
            for content_item in item.get("content", []) if isinstance(item, dict) else []:
                text = content_item.get("text") if isinstance(content_item, dict) else None
                if isinstance(text, str):
                    parts.append(text)
        if parts:
            return "\n".join(parts)
    return ""


def _extract_text_from_response(response: Any, response_dict: dict[str, Any]) -> str:
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text:
        return output_text
    return _extract_response_text(response_dict)


def _finish_status_fields(response_dict: dict[str, Any]) -> dict[str, Any]:
    choices = response_dict.get("choices") or []
    first_choice = choices[0] if choices else {}
    return {
        "finish_reason": first_choice.get("finish_reason"),
        "status": response_dict.get("status"),
        "refusal": (first_choice.get("message") or {}).get("refusal") if first_choice else None,
    }


def _spec_json_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["public_spec", "assumptions", "properties", "edge_cases"],
        "properties": {
            "public_spec": {
                "type": "string",
                "minLength": 1,
                "description": "Concise executable public specification text.",
            },
            "assumptions": {"type": "array", "items": {"type": "string"}},
            "properties": {"type": "array", "items": {"type": "string"}},
            "edge_cases": {"type": "array", "items": {"type": "string"}},
        },
    }


def _is_gpt5_nano(model: str) -> bool:
    return model.startswith("gpt-5-nano")


def _append_debug_raw_response(row: dict[str, Any]) -> None:
    _ensure_results_dir()
    with DEBUG_RAW_OPENAI_RESPONSES_JSONL.open("a", encoding="utf-8") as file:
        file.write(json.dumps(row, ensure_ascii=False) + "\n")


def _parse_generated_payload(text: str) -> tuple[dict[str, Any], str | None]:
    if not text.strip():
        return {}, None
    try:
        parsed = _extract_json(text)
        if isinstance(parsed, dict):
            return parsed, None
        return {"public_spec": text.strip()}, "json_root_not_object"
    except Exception as exc:
        return {"public_spec": text.strip()}, str(exc)


def _normalize_generated_fields(raw: dict[str, Any]) -> dict[str, Any]:
    public_spec = str(raw.get("public_spec", "") or "").strip()
    assumptions = [str(item) for item in raw.get("assumptions", []) if str(item).strip()]
    properties = [str(item) for item in raw.get("properties", []) if str(item).strip()]
    edge_cases = [str(item) for item in raw.get("edge_cases", []) if str(item).strip()]
    generation_empty = not public_spec and not assumptions and not properties and not edge_cases
    return {
        "public_spec": public_spec,
        "assumptions": assumptions,
        "properties": properties,
        "edge_cases": edge_cases,
        "generation_empty": generation_empty,
        "generation_error": "empty_generated_spec" if generation_empty else None,
    }


def _simple_retry_prompt(original_prompt: str) -> str:
    return (
        original_prompt
        + "\n\nReturn plain JSON with public_spec, assumptions, properties, edge_cases. "
        + "Do not leave public_spec empty."
    )


def _debug_row_from_response(
    response: Any,
    model: str,
    task_id: str | None,
    sample_id: int | None,
    attempt: int | str,
    parse_error: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    response_dict = _response_to_dict(response)
    content = _extract_text_from_response(response, response_dict)
    parsed, actual_parse_error = _parse_generated_payload(content)
    normalized = _normalize_generated_fields(parsed)
    debug_row = {
        "timestamp": _timestamp(),
        "model": model,
        "task_id": task_id,
        "sample_id": sample_id,
        "attempt": attempt,
        "raw_response": response_dict,
        "extracted_text": content,
        "parsed_public_spec": normalized["public_spec"],
        "parse_error": parse_error or actual_parse_error,
        "finish_status": _finish_status_fields(response_dict),
        "usage": response_dict.get("usage"),
        "generation_empty": normalized["generation_empty"],
        "generation_error": normalized["generation_error"],
    }
    return debug_row, parsed


def _responses_api_attempts(model: str, prompt: str) -> list[dict[str, Any]]:
    instructions = "Return valid JSON only. Do not wrap the JSON in markdown. Do not leave public_spec empty."
    json_schema_text = {
        "format": {
            "type": "json_schema",
            "name": "public_spec_generation",
            "strict": False,
            "schema": _spec_json_schema(),
        },
        "verbosity": "low",
    }
    json_object_text = {"format": {"type": "json_object"}, "verbosity": "low"}
    return [
        {
            "model": model,
            "instructions": instructions,
            "input": prompt,
            "max_output_tokens": 4000,
            "reasoning": {"effort": "minimal"},
            "text": json_schema_text,
        },
        {
            "model": model,
            "instructions": instructions,
            "input": prompt,
            "max_output_tokens": 4000,
            "reasoning": {"effort": "low"},
            "text": json_schema_text,
        },
        {
            "model": model,
            "instructions": instructions,
            "input": prompt,
            "max_output_tokens": 4000,
            "reasoning": {"effort": "minimal"},
            "text": json_object_text,
        },
        {
            "model": model,
            "instructions": instructions,
            "input": prompt,
            "max_output_tokens": 4000,
            "text": json_object_text,
        },
    ]


def _call_openai_json_responses_api(
    client,
    model: str,
    prompt: str,
    task_id: str | None,
    sample_id: int | None,
    single_attempt: bool = False,
) -> dict[str, Any]:
    last_error = None
    last_debug_row = None
    for attempt_index, kwargs in enumerate(_responses_api_attempts(model, prompt), 1):
        try:
            response = client.responses.create(**kwargs)
            debug_row, parsed = _debug_row_from_response(
                response=response,
                model=model,
                task_id=task_id,
                sample_id=sample_id,
                attempt=f"responses_{attempt_index}",
            )
            _append_debug_raw_response(debug_row)
            last_debug_row = debug_row
            if not debug_row["generation_empty"]:
                return {**parsed, "_debug": debug_row, "_parse_error": debug_row.get("parse_error")}
            if single_attempt:
                return {**parsed, "_debug": debug_row, "_parse_error": debug_row.get("parse_error")}
        except Exception as exc:
            last_error = exc
            if single_attempt:
                raise

    if last_debug_row and last_debug_row.get("generation_empty"):
        retry_response = client.responses.create(
            model=model,
            instructions="Return plain valid JSON only. The public_spec string must be non-empty.",
            input=_simple_retry_prompt(prompt),
            max_output_tokens=4000,
            reasoning={"effort": "minimal"},
            text={"format": {"type": "json_object"}, "verbosity": "low"},
        )
        debug_row, parsed = _debug_row_from_response(
            response=retry_response,
            model=model,
            task_id=task_id,
            sample_id=sample_id,
            attempt="responses_empty_retry",
        )
        _append_debug_raw_response(debug_row)
        return {**parsed, "_debug": debug_row, "_parse_error": debug_row.get("parse_error")}

    raise last_error


def _call_openai_json(
    client,
    model: str,
    prompt: str,
    task_id: str | None = None,
    sample_id: int | None = None,
    single_attempt: bool = False,
) -> dict[str, Any]:
    if _is_gpt5_nano(model):
        return _call_openai_json_responses_api(client, model, prompt, task_id, sample_id, single_attempt)

    messages = [
        {
            "role": "system",
            "content": "Return valid JSON only. Do not wrap the JSON in markdown.",
        },
        {"role": "user", "content": prompt},
    ]
    base_kwargs = {
        "model": model,
        "messages": messages,
        "response_format": {"type": "json_object"},
    }
    attempts = [
        {**base_kwargs, "temperature": 0.7, "max_completion_tokens": 900},
        {**base_kwargs, "max_completion_tokens": 900},
        {**base_kwargs, "temperature": 0.7, "max_tokens": 900},
        {**base_kwargs, "max_tokens": 900},
        {"model": model, "messages": messages, "max_completion_tokens": 900},
    ]

    last_error = None
    last_debug_row = None
    for attempt_index, kwargs in enumerate(attempts, 1):
        try:
            completion = client.chat.completions.create(**kwargs)
            debug_row, parsed = _debug_row_from_response(
                response=completion,
                model=model,
                task_id=task_id,
                sample_id=sample_id,
                attempt=attempt_index,
            )
            _append_debug_raw_response(debug_row)
            last_debug_row = debug_row
            if not debug_row["generation_empty"]:
                return {**parsed, "_debug": debug_row, "_parse_error": debug_row.get("parse_error")}
            if single_attempt:
                return {**parsed, "_debug": debug_row, "_parse_error": debug_row.get("parse_error")}
            break
        except Exception as exc:  # SDK/model parameter compatibility fallback.
            last_error = exc
            if single_attempt:
                raise

    if last_debug_row and last_debug_row.get("generation_empty"):
        retry_messages = [
            {
                "role": "system",
                "content": "Return plain valid JSON only. Do not leave public_spec empty.",
            },
            {"role": "user", "content": _simple_retry_prompt(prompt)},
        ]
        retry_kwargs = {"model": model, "messages": retry_messages, "max_completion_tokens": 900}
        completion = client.chat.completions.create(**retry_kwargs)
        debug_row, parsed = _debug_row_from_response(
            response=completion,
            model=model,
            task_id=task_id,
            sample_id=sample_id,
            attempt="empty_retry",
        )
        _append_debug_raw_response(debug_row)
        return {**parsed, "_debug": debug_row, "_parse_error": debug_row.get("parse_error")}

    raise last_error


def generate_spec_with_openai(task: dict, sample_id: int, model: str, single_attempt: bool = False) -> dict:
    client = get_openai_client()
    prompt = f"""
You are writing a public executable specification for a spec-driven code generation pipeline.
Given the user intent, write a concise but precise specification.

Task title: {task["title"]}
Function entrypoint: {task["entrypoint"]}
User intent:
{task["intent"]}

Include:
- normal behavior
- boundary behavior
- invalid input behavior
- state updates or invariants if relevant
- security/authorization rules if relevant
- temporal rules if relevant

Return JSON only:
{{
  "public_spec": "...",
  "assumptions": ["..."],
  "properties": ["..."],
  "edge_cases": ["..."]
}}
""".strip()
    raw = _call_openai_json(
        client,
        model,
        prompt,
        task_id=task["id"],
        sample_id=sample_id,
        single_attempt=single_attempt,
    )
    fields = _normalize_generated_fields(raw)
    return {
        "provider_configured": True,
        "timestamp": _timestamp(),
        "task_id": task["id"],
        "task_title": task["title"],
        "sample_id": sample_id,
        "model": model,
        "public_spec": fields["public_spec"],
        "assumptions": fields["assumptions"],
        "properties": fields["properties"],
        "edge_cases": fields["edge_cases"],
        "generation_empty": fields["generation_empty"],
        "generation_error": fields["generation_error"],
        "parse_error": raw.get("_parse_error"),
        "raw_response_debug_path": str(DEBUG_RAW_OPENAI_RESPONSES_JSONL.relative_to(BASE_DIR)),
        "raw": raw,
    }


def debug_one_spec_generation(task_id: str = "refund_double_refund", model: str | None = None) -> dict:
    model = _default_model(model)
    task = load_task(task_id)
    generated = generate_spec_with_openai(task, sample_id=1, model=model, single_attempt=True)
    return {
        "model": generated["model"],
        "task_id": generated["task_id"],
        "generated_public_spec": generated["public_spec"],
        "assumptions": generated["assumptions"],
        "properties": generated["properties"],
        "edge_cases": generated["edge_cases"],
        "generation_empty": generated["generation_empty"],
        "generation_error": generated["generation_error"],
        "raw_response_debug_path": generated["raw_response_debug_path"],
    }


def _keyword_rules() -> dict[str, dict[str, list[str]]]:
    return {
        "refund_double_refund": {
            "Refund must not exceed original payment": [
                "original payment",
                "exceed payment",
                "exceeds payment",
                "remaining balance",
                "over refund",
                "over-refund",
                "refundable balance",
            ],
            "Same order cannot be refunded twice": [
                "double refund",
                "same order",
                "already refunded",
                "remaining refundable",
                "refunded_total",
                "cannot be refunded twice",
                "refunded twice",
            ],
            "Invalid or cancelled orders must fail": [
                "invalid order",
                "cancelled",
                "canceled",
                "status",
                "paid",
                "must fail",
            ],
            "Refunded state must be updated after successful refund": [
                "update refunded",
                "refunded_total",
                "state",
                "updated order",
                "record refund",
                "increment refunded",
            ],
        },
        "access_control_delete_user": {
            "Only admins may delete users": ["only admin", "only admins", "admin", "administrator"],
            "Members and guests must be rejected": ["member", "guest", "non-admin", "non admin", "rejected"],
            "Users cannot delete themselves": ["self delete", "delete themselves", "same user", "actor", "target"],
            "Missing target users must fail": ["missing target", "target exists", "invalid target", "target user"],
            "Deleted state must be updated": ["status", "deleted", "mark deleted", "state"],
        },
        "discount_nonnegative_price": {
            "Price must be non negative": ["non negative price", "non-negative price", "price >= 0", "price must not be negative"],
            "Discount percent must be between 0 and 100": ["between 0 and 100", "0 to 100", "0 and 100", "percent <= 100", "percent must not exceed 100"],
            "Final price must never be negative": ["final price", "never negative", "not be negative", "below zero"],
            "Invalid input should fail": ["invalid", "error", "reject", "fail"],
        },
        "rate_limiter_boundary": {
            "The 6th request must be blocked": ["6th", "sixth", "at most 5", "limit exceeded", "blocked"],
            "The limit is per user, not global": ["per user", "different users", "independent", "not global"],
            "Old requests outside 60 seconds must expire": ["60 second", "60-second", "outside 60", "expire", "rolling window"],
            "Boundary behavior at exactly 5 requests must be correct": ["exactly 5", "at most 5", "boundary", "5 requests"],
        },
        "expiry_handle_today": {
            "Category lead time must be applied": ["lead time", "category_lead_time", "subtract", "minus"],
            "Items that should have been handled earlier are still handle_today": ["earlier", "today or earlier", "before today", "already should"],
            "Already expired items must be handled": ["expired", "past expiry", "already expired"],
            "Invalid date input must fail": ["invalid date", "parse", "error", "fail"],
            "Boundary condition uses today or earlier, not only exact equality": ["today or earlier", "<=", "on or before", "boundary"],
        },
        "payment_webhook_idempotency": {
            "The same event_id must not be credited twice": [
                "idempotent",
                "idempotency",
                "duplicate event",
                "duplicate webhook",
                "same event_id",
                "already processed",
                "process once",
                "credited twice",
                "double credit",
                "repeated event",
            ],
            "Missing event_id must fail": [
                "missing event_id",
                "require event_id",
                "event_id must be present",
                "event_id is required",
            ],
            "Amount must be positive": [
                "amount positive",
                "positive amount",
                "non-positive amount",
                "amount > 0",
                "amount must be greater than 0",
            ],
            "Unsupported currency must fail": [
                "currency",
                "supported currency",
                "SEK",
                "unsupported currency",
            ],
            "Failed payments must not credit balance": [
                "failed payment",
                "failed events",
                "must not increase balance",
                "no balance change for failed",
                "failed payments should not increase",
            ],
            "Processed successful event IDs must be recorded": [
                "record event_id",
                "store event_id",
                "processed_event_ids",
                "mark event as processed",
                "already processed",
            ],
        },
        "refund_window_expiry": {
            "Refunds are only allowed within 30 days of purchase unless manual_override is true": [
                "30 days",
                "within 30 days",
                "refund window",
                "purchase date",
                "days since purchase",
                "after purchase",
                "refund period",
            ],
            "Day 30 is still allowed but day 31 is rejected without manual_override": [
                "day 30",
                "30th day",
                "day 31",
                "more than 30 days",
                "boundary",
                "inclusive",
            ],
            "Manual override permits refunds after the normal window": [
                "manual_override",
                "manual override",
                "override",
                "exception approval",
            ],
            "Cancelled or chargeback orders cannot be refunded": [
                "cancelled",
                "canceled",
                "chargeback",
                "invalid status",
                "only paid orders",
            ],
            "Successful refunds must update refunded_total": [
                "refunded_total",
                "update refunded total",
                "remaining amount",
                "remaining refundable",
                "prior refunds",
            ],
        },
        "loyalty_refund_reversal": {
            "Successful refunds must reverse proportional loyalty points awarded by the original purchase": [
                "loyalty",
                "loyalty points",
                "reward points",
                "points reversal",
                "reverse awarded points",
                "proportional points",
                "customer balance",
                "proportional",
                "pro rata",
                "refunded portion",
                "partial refund points",
            ],
            "Loyalty points must not become negative": [
                "not negative",
                "never below zero",
                "non-negative points",
                "non negative points",
                "loyalty points must not become negative",
            ],
            "Cancelled or chargeback orders cannot be refunded": [
                "cancelled",
                "canceled",
                "chargeback",
                "invalid status",
                "only paid orders",
            ],
            "Successful refunds must update refunded_total": [
                "refunded_total",
                "update refunded total",
                "remaining amount",
                "remaining refundable",
                "prior refunds",
            ],
            "Refund cannot exceed remaining paid amount": [
                "remaining paid amount",
                "remaining amount",
                "cannot exceed",
                "original payment",
                "over refund",
                "over-refund",
            ],
        },
    }


def _unclear_terms(requirement: str) -> list[str]:
    words = [
        word.lower()
        for word in requirement.replace("-", " ").replace("_", " ").split()
        if len(word) >= 5
    ]
    return words[:4]


def analyze_spec_coverage(task: dict, generated_spec_text: str) -> dict:
    text = generated_spec_text.lower()
    rules = _keyword_rules().get(task["id"], {})
    coverage = []
    missing_categories = set()

    for requirement in task.get("missing_requirements", []):
        keywords = rules.get(requirement, [])
        matched = [keyword for keyword in keywords if keyword.lower() in text]
        unclear_matches = [term for term in _unclear_terms(requirement) if term in text]

        if matched:
            status = "covered"
            evidence = ", ".join(matched[:3])
        elif unclear_matches:
            status = "unclear"
            evidence = "mentions related term(s): " + ", ".join(unclear_matches[:3])
            missing_categories.update(task.get("spec_hole_categories", []))
        else:
            status = "missing"
            evidence = "No matching requirement keywords found."
            missing_categories.update(task.get("spec_hole_categories", []))

        coverage.append({"requirement": requirement, "status": status, "evidence": evidence})

    covered_count = sum(1 for item in coverage if item["status"] == "covered")
    missing_count = sum(1 for item in coverage if item["status"] == "missing")
    unclear_count = sum(1 for item in coverage if item["status"] == "unclear")
    total = len(coverage)

    return {
        "coverage": coverage,
        "covered_count": covered_count,
        "missing_count": missing_count,
        "unclear_count": unclear_count,
        "not_clearly_covered_count": missing_count + unclear_count,
        "clear_coverage_rate": covered_count / total if total else 0.0,
        "possible_coverage_rate": (covered_count + unclear_count) / total if total else 0.0,
        "coverage_rate": covered_count / total if total else 0.0,
        "missing_categories": sorted(missing_categories),
        "not_clearly_covered_categories": sorted(missing_categories),
    }


def _append_llm_run(row: dict[str, Any]) -> None:
    _ensure_results_dir()
    with LLM_SPEC_RUNS_JSONL.open("a", encoding="utf-8") as file:
        file.write(json.dumps(row, ensure_ascii=False) + "\n")


def generate_specs_for_task(task_id: str, num_samples: int = 5, model: str | None = None) -> dict:
    model = _default_model(model)
    task = load_task(task_id)
    try:
        get_openai_client()
    except ProviderNotConfigured as exc:
        return {"provider_configured": False, "error": str(exc), "task_id": task_id, "model": model}

    samples = []
    for sample_id in range(1, num_samples + 1):
        generated = generate_spec_with_openai(task, sample_id, model)
        analysis = analyze_spec_coverage(task, generated["public_spec"])
        row = {**generated, "analysis": analysis}
        _append_llm_run(row)
        samples.append(row)

    return {
        "provider_configured": True,
        "timestamp": _timestamp(),
        "task_id": task["id"],
        "task_title": task["title"],
        "intent": task["intent"],
        "model": model,
        "num_samples": num_samples,
        "samples": samples,
    }


def run_llm_spec_experiment(num_samples_per_task: int = 5, model: str | None = None) -> dict:
    model = _default_model(model)
    try:
        get_openai_client()
    except ProviderNotConfigured as exc:
        return {"provider_configured": False, "error": str(exc), "model": model}

    task_results = []
    all_samples = []
    not_clear_category_counter: Counter[str] = Counter()
    exact_missing_category_counter: Counter[str] = Counter()
    unclear_category_counter: Counter[str] = Counter()

    for task in list_tasks():
        task_result = generate_specs_for_task(task["id"], num_samples_per_task, model)
        task_results.append(task_result)
        for sample in task_result.get("samples", []):
            all_samples.append(sample)
            analysis = sample["analysis"]
            categories = analysis.get("not_clearly_covered_categories") or analysis.get("missing_categories", [])
            if analysis.get("missing_count", 0) or analysis.get("unclear_count", 0):
                not_clear_category_counter.update(categories)
            if analysis.get("missing_count", 0):
                exact_missing_category_counter.update(categories)
            if analysis.get("unclear_count", 0):
                unclear_category_counter.update(categories)

    summary = summarize_llm_samples(all_samples)
    experiment = {
        "provider_configured": True,
        "timestamp": _timestamp(),
        "model": model,
        "total_tasks": len(task_results),
        "samples_per_task": num_samples_per_task,
        "total_specs": summary["total_specs"],
        "average_clear_coverage_rate": summary["average_clear_coverage_rate"],
        "average_possible_coverage_rate": summary["average_possible_coverage_rate"],
        "average_coverage_rate": summary["average_clear_coverage_rate"],
        "exact_missing_requirements": summary["exact_missing_requirements"],
        "unclear_requirements": summary["unclear_requirements"],
        "not_clearly_covered_requirements": summary["not_clearly_covered_requirements"],
        "total_missing_requirements": summary["exact_missing_requirements"],
        "most_common_not_clearly_covered_categories": dict(not_clear_category_counter.most_common()),
        "most_common_exact_missing_categories": dict(exact_missing_category_counter.most_common()),
        "most_common_unclear_categories": dict(unclear_category_counter.most_common()),
        "task_results": task_results,
    }
    _ensure_results_dir()
    with LLM_SPEC_LATEST_JSON.open("w", encoding="utf-8") as file:
        json.dump(experiment, file, indent=2, ensure_ascii=False)
    return experiment


def summarize_llm_samples(samples: list[dict[str, Any]]) -> dict[str, Any]:
    total_specs = len(samples)
    exact_missing = sum(sample["analysis"].get("missing_count", 0) for sample in samples)
    unclear = sum(sample["analysis"].get("unclear_count", 0) for sample in samples)
    average_clear = (
        sum(sample["analysis"].get("clear_coverage_rate", sample["analysis"].get("coverage_rate", 0.0)) for sample in samples)
        / total_specs
        if total_specs
        else 0.0
    )
    average_possible = (
        sum(
            sample["analysis"].get(
                "possible_coverage_rate",
                (
                    sample["analysis"].get("covered_count", 0)
                    + sample["analysis"].get("unclear_count", 0)
                )
                / max(
                    1,
                    sample["analysis"].get("covered_count", 0)
                    + sample["analysis"].get("missing_count", 0)
                    + sample["analysis"].get("unclear_count", 0),
                ),
            )
            for sample in samples
        )
        / total_specs
        if total_specs
        else 0.0
    )
    return {
        "total_specs": total_specs,
        "exact_missing_requirements": exact_missing,
        "unclear_requirements": unclear,
        "not_clearly_covered_requirements": exact_missing + unclear,
        "average_clear_coverage_rate": average_clear,
        "average_possible_coverage_rate": average_possible,
    }


def _category_counters_for_samples(samples: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    not_clear_counter: Counter[str] = Counter()
    exact_missing_counter: Counter[str] = Counter()
    unclear_counter: Counter[str] = Counter()

    for sample in samples:
        analysis = sample.get("analysis", {})
        categories = analysis.get("not_clearly_covered_categories") or analysis.get("missing_categories", [])
        if analysis.get("missing_count", 0) or analysis.get("unclear_count", 0):
            not_clear_counter.update(categories)
        if analysis.get("missing_count", 0):
            exact_missing_counter.update(categories)
        if analysis.get("unclear_count", 0):
            unclear_counter.update(categories)

    return {
        "most_common_not_clearly_covered_categories": dict(not_clear_counter.most_common()),
        "most_common_exact_missing_categories": dict(exact_missing_counter.most_common()),
        "most_common_unclear_categories": dict(unclear_counter.most_common()),
    }


def _is_valid_llm_generation(row: dict[str, Any]) -> bool:
    if row.get("generation_empty") is True:
        return False
    if row.get("generation_error") == "empty_generated_spec":
        return False
    if not str(row.get("public_spec") or "").strip():
        return False
    return True


def _load_llm_spec_run_rows() -> list[dict[str, Any]]:
    if not LLM_SPEC_RUNS_JSONL.exists():
        return []

    rows = []
    with LLM_SPEC_RUNS_JSONL.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def build_llm_model_comparison() -> dict:
    rows = _load_llm_spec_run_rows()
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        model = row.get("model") or "unknown"
        grouped.setdefault(model, []).append(row)

    model_rows = []
    for model, saved_rows in sorted(grouped.items()):
        valid_samples = [row for row in saved_rows if _is_valid_llm_generation(row)]
        invalid_generations = len(saved_rows) - len(valid_samples)
        summary = summarize_llm_samples(valid_samples)
        category_counts = _category_counters_for_samples(valid_samples)
        model_rows.append(
            {
                "model": model,
                "valid_specs": len(valid_samples),
                "invalid_generations": invalid_generations,
                "total_saved_rows": len(saved_rows),
                **summary,
                **category_counts,
            }
        )

    comparison = {
        "timestamp": _timestamp(),
        "source": str(LLM_SPEC_RUNS_JSONL.relative_to(BASE_DIR)),
        "total_models": len(model_rows),
        "total_specs": len(rows),
        "models": model_rows,
    }
    _ensure_results_dir()
    with LLM_MODEL_COMPARISON_LATEST_JSON.open("w", encoding="utf-8") as file:
        json.dump(comparison, file, indent=2, ensure_ascii=False)
    return comparison


def load_llm_model_comparison() -> dict | None:
    if not LLM_MODEL_COMPARISON_LATEST_JSON.exists():
        return None
    with LLM_MODEL_COMPARISON_LATEST_JSON.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_latest_llm_spec_experiment() -> dict | None:
    if not LLM_SPEC_LATEST_JSON.exists():
        return None
    with LLM_SPEC_LATEST_JSON.open("r", encoding="utf-8") as file:
        return json.load(file)
