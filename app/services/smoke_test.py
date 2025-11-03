from openai import OpenAI
client = OpenAI(api_key="YOUR_API_KEY")  # temp only
print(client.responses.create(model="gpt-4o-mini", input="ping").output_text)



# """OpenAI Responses API integration for extracting shopping list items (no strict schema)."""
# from __future__ import annotations
#
# import json
# import re
# from typing import Any, Dict, Tuple
#
# from openai import OpenAI
#
# # --- Prompt tuned for kit → components, gentle guidance only (no hard schema) ---
# SYSTEM_PROMPT = (
#     "You are a procurement assistant for industrial supplies on grainger.com.\n"
#     "Convert the user's natural-language intent into a JSON object describing items to buy.\n"
#     "\n"
#     "Rules:\n"
#     "• If the user mentions a kit/bundle/category (e.g., 'PPE kit'), expand into minimal sensible components as separate items.\n"
#     "• Use generic names when brand/part_number are not given. Do not invent brands or part numbers.\n"
#     "• Keep quantities integer; if missing, default to 1. Preserve sizes/specs if mentioned.\n"
#     "• Deduplicate overlapping items by consolidating quantities.\n"
#     "• Return ONLY a single JSON object with an 'items' array. No prose, no explanations.\n"
#     "\n"
#     "Example return shape (not enforced):\n"
#     "{\n"
#     "  \"items\": [\n"
#     "    {\"query\": \"nitrile gloves size L\", \"quantity\": 3},\n"
#     "    {\"query\": \"safety goggles anti-fog\", \"quantity\": 3}\n"
#     "  ]\n"
#     "}"
# )
#
# _client: OpenAI | None = None
#
# def _get_client() -> OpenAI:
#     global _client
#     if _client is None:
#         _client = OpenAI()
#     return _client
#
# def _extract_json_block(txt: str) -> Tuple[Dict[str, Any], str]:
#     """
#     Try multiple strategies to pull a JSON object out of model text:
#     1) Direct json.loads on the whole text.
#     2) Parse the first ```json ... ``` fenced block.
#     3) Fallback: find the first top-level {...} using a simple brace matcher.
#     Returns (parsed_dict, raw_fragment).
#     Raises ValueError if nothing parseable is found.
#     """
#     # 1) Direct
#     try:
#         return json.loads(txt), txt
#     except Exception:
#         pass
#
#     # 2) ```json fenced block
#     fence = re.search(r"```json\s*(\{.*?\})\s*```", txt, flags=re.DOTALL | re.IGNORECASE)
#     if fence:
#         block = fence.group(1).strip()
#         try:
#             return json.loads(block), block
#         except Exception:
#             pass
#
#     # 3) First top-level {...} by brace balancing
#     start = txt.find("{")
#     if start != -1:
#         depth = 0
#         for i in range(start, len(txt)):
#             ch = txt[i]
#             if ch == "{":
#                 depth += 1
#             elif ch == "}":
#                 depth -= 1
#                 if depth == 0:
#                     candidate = txt[start : i + 1]
#                     try:
#                         return json.loads(candidate), candidate
#                     except Exception:
#                         break
#
#     raise ValueError("Could not extract valid JSON from model output.")
#
# def _normalize_items(obj: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     Make the output easy for the UI:
#     - Ensure 'items' is a list.
#     - Coerce quantity to int >= 1 (default 1).
#     - Ensure 'query' is a non-empty string; drop items without it.
#     - Preserve any extra fields the model may include.
#     """
#     items = obj.get("items", [])
#     if not isinstance(items, list):
#         items = []
#
#     norm = []
#     for it in items:
#         if not isinstance(it, dict):
#             continue
#         query = str(it.get("query", "")).strip()
#         if not query:
#             continue
#         q = it.get("quantity", 1)
#         try:
#             q = int(q)
#         except Exception:
#             q = 1
#         if q < 1:
#             q = 1
#         it["query"] = query
#         it["quantity"] = q
#         norm.append(it)
#
#     obj["items"] = norm
#     return obj
#
# def extract_items(text: str) -> Dict[str, Any]:
#     """Call OpenAI to turn free-form text into a JSON object (schema not enforced)."""
#     if not text.strip():
#         raise ValueError("Input text cannot be empty.")
#
#     client = _get_client()
#
#     try:
#         response = client.responses.create(
#             model="gpt-4.1-mini",
#             input=[
#                 {"role": "system", "content": [{"type": "input_text", "text": SYSTEM_PROMPT}]},
#                 {"role": "user", "content": [{"type": "input_text", "text": text.strip()}]},
#             ],
#             # NOTE: No response_format here (we're not enforcing a schema)
#         )
#     except Exception as exc:  # pragma: no cover
#         raise RuntimeError(f"OpenAI request failed: {exc}") from exc
#
#     # Prefer output_text; if missing, fall back to concatenating output content.
#     raw_text = getattr(response, "output_text", None)
#     if not raw_text:
#         # Some SDK versions expose 'output' parts; stitch as text for robustness.
#         if getattr(response, "output", None):
#             try:
#                 raw_text = "".join(
#                     p.content[0].text.value
#                     for p in response.output
#                     if getattr(p, "content", None) and getattr(p.content[0], "text", None)
#                 )
#             except Exception:
#                 pass
#     if not raw_text:
#         raise RuntimeError("Received empty response from OpenAI.")
#
#     try:
#         parsed, fragment = _extract_json_block(raw_text)
#     except ValueError as exc:
#         # Surface first 500 chars to help debugging in the UI
#         preview = raw_text[:500]
#         raise RuntimeError(f"Failed to parse JSON from model output.\nPreview:\n{preview}") from exc
#
#     normalized = _normalize_items(parsed)
#     # Optionally include the fragment for a hidden debug panel in your UI
#     return {"items": normalized.get("items", []), "_raw": fragment}
