"""Minimal OpenAI call for shopping list extraction (no strict schema)."""
from __future__ import annotations
import json, os
from typing import Any, Dict
from openai import OpenAI

# --- Prompt tuned for kit → components, gentle guidance only (no hard schema) ---
SYSTEM_PROMPT = (
    "You are a procurement assistant for industrial supplies on grainger.com.\n"
    "Convert the user's natural-language intent into a JSON object describing items to buy.\n"
    "\n"
    "Rules:\n"
    "• If the user mentions a kit/bundle/category (e.g., 'PPE kit'), expand into minimal sensible components as separate items.\n"
    "• Use generic names when brand/part_number are not given. Do not invent brands or part numbers.\n"
    "• Keep quantities integer; if missing, default to 1. Preserve sizes/specs if mentioned.\n"
    "• Deduplicate overlapping items by consolidating quantities.\n"
    "• Return ONLY a single JSON object with an 'items' array. No prose, no explanations.\n"
    "\n"
    "Example return shape (not enforced):\n"
    "{\n"
    "  \"items\": [\n"
    "    {\"query\": \"nitrile gloves size L\", \"quantity\": 3},\n"
    "    {\"query\": \"safety goggles anti-fog\", \"quantity\": 3}\n"
    "  ]\n"
    "}"
)

_client: OpenAI | None = None
def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client

def extract_items(text: str) -> Dict[str, Any]:
    if not text.strip():
        raise ValueError("Input text cannot be empty.")

    client = _get_client()
    resp = client.responses.create(
        model="gpt-4o-mini",  # or gpt-4o / gpt-4.1-mini
        input=[
            {"role": "system", "content": [{"type": "input_text", "text": SYSTEM_PROMPT}]},
            {"role": "user",   "content": [{"type": "input_text", "text": text.strip()}]},
        ],
    )

    raw = resp.output_text  # should be a JSON string per our instruction
    try:
        data = json.loads(raw)
    except Exception:
        # If the model ever wraps in ```json ... ```, strip it quickly:
        cleaned = raw.strip().removeprefix("```json").removesuffix("```").strip()
        data = json.loads(cleaned)

    # super-light normalization for table safety
    items = data.get("items", []) if isinstance(data, dict) else []
    norm = []
    for it in items if isinstance(items, list) else []:
        if not isinstance(it, dict):
            continue
        q = it.get("quantity", 1)
        try: q = int(q)
        except: q = 1
        norm.append({"query": (it.get("query") or "").strip(), "quantity": max(q, 1), **{k:v for k,v in it.items() if k not in ("query","quantity")}})
    return {"items": [x for x in norm if x["query"]]}
