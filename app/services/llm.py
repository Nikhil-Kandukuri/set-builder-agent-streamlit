"""OpenAI Responses API integration for extracting shopping list items."""
from __future__ import annotations

import json
from typing import Any, Dict

from openai import OpenAI

from .schemas import SHOPPING_LIST_JSON_SCHEMA, ShoppingList

SYSTEM_PROMPT = (
    "Extract a structured shopping list for grainger.com from the user text. "
    "Prefer brand/part_number if present; infer reasonable quantity if missing; "
    "never hallucinate."
)

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def extract_items(text: str) -> Dict[str, Any]:
    """Call OpenAI to extract structured shopping items from free-form text."""
    if not text.strip():
        raise ValueError("Input text cannot be empty.")

    client = _get_client()

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": [{"type": "text", "text": SYSTEM_PROMPT}],
                },
                {"role": "user", "content": [{"type": "text", "text": text.strip()}]},
            ],
            response_format={"type": "json_schema", "json_schema": SHOPPING_LIST_JSON_SCHEMA},
        )
    except Exception as exc:  # pragma: no cover - network/SDK errors
        raise RuntimeError(f"OpenAI request failed: {exc}") from exc

    if not getattr(response, "output", None):
        raise RuntimeError("Received empty response from OpenAI.")

    try:
        parsed = json.loads(response.output_text)
    except (TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Failed to parse response JSON.") from exc

    try:
        validated = ShoppingList.model_validate(parsed)
    except Exception as exc:  # pragma: no cover - validation errors
        raise RuntimeError(f"Response did not match schema: {exc}") from exc

    return validated.model_dump()
