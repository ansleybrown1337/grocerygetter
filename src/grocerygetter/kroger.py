"""Kroger API adapter boundaries.

The Streamlit app currently uses this module to build a reviewed cart payload.
Live API calls are kept behind KrogerClient so recipe planning can be tested
without credentials or network access.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import GroceryItem, ProductMapping


@dataclass(frozen=True)
class CartPayloadItem:
    upc: str
    quantity: int
    modality: str = "PICKUP"


def build_cart_payload(
    grocery_items: list[GroceryItem],
    mappings: dict[tuple[str, str], ProductMapping],
) -> dict[str, list[dict[str, str | int]]]:
    """Build the Kroger cart payload from reviewed product mappings."""

    payload_items: list[dict[str, str | int]] = []
    for item in grocery_items:
        mapping = mappings.get((item.ingredient_name, item.unit))
        if mapping is None or not mapping.upc:
            continue
        payload_items.append(
            {
                "upc": mapping.upc,
                "quantity": max(1, int(mapping.cart_quantity)),
                "modality": mapping.modality,
            }
        )
    return {"items": payload_items}


class KrogerClient:
    """Thin client for future live Kroger integration."""

    def __init__(self, access_token: str, *, base_url: str = "https://api.kroger.com/v1"):
        self.access_token = access_token
        self.base_url = base_url.rstrip("/")

    def search_products(
        self,
        term: str,
        *,
        location_id: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        params: dict[str, str | int] = {
            "filter.term": term,
            "filter.limit": limit,
        }
        if location_id:
            params["filter.locationId"] = location_id

        import requests

        response = requests.get(
            f"{self.base_url}/products",
            headers=self._headers(),
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return list(response.json().get("data", []))

    def add_to_cart(self, items: list[CartPayloadItem]) -> dict[str, Any]:
        import requests

        payload = {
            "items": [
                {
                    "upc": item.upc,
                    "quantity": item.quantity,
                    "modality": item.modality,
                }
                for item in items
            ]
        }
        response = requests.put(
            f"{self.base_url}/cart/add",
            headers={**self._headers(), "Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        if not response.content:
            return {}
        return dict(response.json())

    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }
