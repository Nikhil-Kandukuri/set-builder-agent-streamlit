"""Streamlit frontend for the shopping list demo app."""
from __future__ import annotations

import json
from typing import Any, Dict, List

import streamlit as st
from dotenv import load_dotenv

from services.llm import extract_items
from services.schemas import ShoppingList
from tools.cart_stub import add_items_to_cart

load_dotenv()

st.set_page_config(page_title="Shopping List Demo", page_icon="🛒", layout="centered")
st.title("Shopping List Demo")
st.caption("Enter a request and let the AI structure it for grainger.com shopping.")

if "shopping_items" not in st.session_state:
    st.session_state["shopping_items"] = None
if "raw_shopping_list" not in st.session_state:
    st.session_state["raw_shopping_list"] = None
if "cart_result" not in st.session_state:
    st.session_state["cart_result"] = None

user_input = st.text_area(
    "Describe what you need",
    placeholder="e.g., 3× WD-40 11oz, 2× nitrile gloves size L",
    height=160,
)

if st.button("Understand", use_container_width=True):
    if not user_input.strip():
        st.warning("Please provide a description before running the extractor.")
    else:
        with st.spinner("Understanding your request..."):
            try:
                result = extract_items(user_input)
            except Exception as exc:  # pragma: no cover - UI error handling
                st.session_state["shopping_items"] = None
                st.session_state["raw_shopping_list"] = None
                st.session_state["cart_result"] = None
                st.error(str(exc))
            else:
                validated = ShoppingList.model_validate(result)
                st.session_state["shopping_items"] = [
                    item.model_dump() for item in validated.items
                ]
                st.session_state["raw_shopping_list"] = validated.model_dump()
                st.session_state["cart_result"] = None
                st.success("Shopping list extracted successfully.")

items: List[Dict[str, Any]] = st.session_state.get("shopping_items") or []
raw_payload = st.session_state.get("raw_shopping_list")

if raw_payload:
    st.subheader("Structured Output")
    st.code(json.dumps(raw_payload, indent=2), language="json")

if items:
    st.subheader("Items")
    st.table(items)

    if st.button("Add to Cart (stub)", use_container_width=True):
        with st.spinner("Calling cart integration stub..."):
            st.session_state["cart_result"] = add_items_to_cart(items)

cart_result = st.session_state.get("cart_result")
if cart_result:
    st.info(cart_result["message"])
    st.json(cart_result)
