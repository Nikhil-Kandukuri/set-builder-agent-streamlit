"""Streamlit frontend for the shopping list demo app (no Pydantic)."""
from __future__ import annotations

import json
from typing import Any, Dict, List

import streamlit as st
from dotenv import load_dotenv

from services.llm import extract_items
from tools.cart_stub import add_items_to_cart

load_dotenv()

st.set_page_config(page_title="Shopping List Demo", page_icon="🛒", layout="centered")
st.title("Shopping List Demo")
st.caption("Enter a request and let the AI structure it for grainger.com shopping.")

# ---- Session state ----
st.session_state.setdefault("shopping_items", None)
st.session_state.setdefault("raw_fragment", None)
st.session_state.setdefault("cart_result", None)

# ---- Input ----
with st.form("nl_form"):
    user_input = st.text_area(
        "Describe what you need",
        placeholder="e.g., 3× WD-40 11oz, 2× nitrile gloves size L",
        height=160,
    )
    submitted = st.form_submit_button("Understand", use_container_width=True)

# ---- Run extraction ----
if submitted:
    if not user_input.strip():
        st.warning("Please provide a description before running the extractor.")
    else:
        with st.spinner("Understanding your request..."):
            try:
                result = extract_items(user_input)  # returns {"items":[...], "_raw": "..."}
                items = result.get("items", [])
                st.session_state["shopping_items"] = items
                st.session_state["raw_fragment"] = result.get("_raw")
                st.session_state["cart_result"] = None
                st.success("Shopping list extracted successfully.")
            except Exception as exc:
                st.session_state["shopping_items"] = None
                st.session_state["raw_fragment"] = None
                st.session_state["cart_result"] = None
                st.error(f"Extractor error: {exc}")

# ---- Output ----
items: List[Dict[str, Any]] = st.session_state.get("shopping_items") or []
raw_fragment = st.session_state.get("raw_fragment")

if items:
    st.subheader("Items")
    # Normalize for display (ensure keys exist)
    display_rows = [
        {
            "query": (it.get("query") or ""),
            "quantity": int(it.get("quantity", 1)),
            **{k: v for k, v in it.items() if k not in ("query", "quantity")},
        }
        for it in items
        if isinstance(it, dict)
    ]
    st.dataframe(display_rows, use_container_width=True)

    if st.button("Add to Cart (stub)", use_container_width=True):
        with st.spinner("Calling cart integration stub..."):
            st.session_state["cart_result"] = add_items_to_cart(items)

if raw_fragment:
    with st.expander("Debug: Raw JSON fragment from model"):
        st.code(raw_fragment, language="json")

cart_result = st.session_state.get("cart_result")
if cart_result:
    st.info(cart_result.get("message", "Cart stub result"))
    st.json(cart_result)
