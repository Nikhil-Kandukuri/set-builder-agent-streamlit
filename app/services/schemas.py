"""Schemas and models for shopping list extraction."""
from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict, Field


class ShoppingItem(BaseModel):
    """Single item entry in a shopping list."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(..., description="Original text describing the item")
    quantity: int = Field(..., ge=1, description="Quantity requested for the item")
    brand: str = Field("", description="Brand name if provided")
    part_number: str = Field(
        "", description="Manufacturer or supplier part number when available"
    )


class ShoppingList(BaseModel):
    """Structured list of shopping items."""

    model_config = ConfigDict(extra="forbid")

    items: List[ShoppingItem]


SHOPPING_LIST_JSON_SCHEMA = {
    "name": "shopping_list",
    "schema": {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "quantity": {"type": "integer", "minimum": 1},
                        "brand": {"type": "string"},
                        "part_number": {"type": "string"},
                    },
                    "required": ["query", "quantity"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["items"],
        "additionalProperties": False,
    },
    "strict": True,
}
"""JSON schema definition used for Responses API structured output."""
