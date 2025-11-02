"""Stub for future cart integration."""
from __future__ import annotations

from typing import Any, Dict, List


def add_items_to_cart(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Placeholder cart integration that echoes back received items."""
    return {
        "ok": True,
        "message": "Cart flow not wired yet",
        "received": items,
    }
