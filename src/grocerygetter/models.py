"""Domain models for recipes, meal plans, grocery lists, and product mappings."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RecipeSummary:
    id: int
    name: str
    servings: float
    source: str | None = None


@dataclass(frozen=True)
class RecipeIngredient:
    id: int | None
    recipe_id: int | None
    raw_text: str
    ingredient_name: str
    quantity: float
    unit: str
    preparation: str | None = None
    sort_order: int = 0


@dataclass(frozen=True)
class Recipe:
    id: int | None
    name: str
    servings: float
    ingredients: tuple[RecipeIngredient, ...] = field(default_factory=tuple)
    steps: tuple[str, ...] = field(default_factory=tuple)
    source: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class MealSelection:
    recipe_id: int
    scale: float = 1.0


@dataclass(frozen=True)
class GroceryItem:
    ingredient_name: str
    quantity: float
    unit: str
    recipe_sources: tuple[str, ...]
    raw_items: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ProductMapping:
    ingredient_name: str
    unit: str
    product_name: str
    upc: str
    cart_quantity: int = 1
    brand: str | None = None
    package_size: str | None = None
    location_id: str = ""
    modality: str = "PICKUP"
