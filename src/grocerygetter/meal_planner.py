"""Meal-plan aggregation logic."""

from __future__ import annotations

from collections import defaultdict

from .models import GroceryItem, MealSelection
from .repository import RecipeRepository
from .units import normalize_ingredient_name, quantity_for_aggregation


def build_grocery_list(
    repository: RecipeRepository,
    selections: list[MealSelection],
) -> list[GroceryItem]:
    """Aggregate ingredients across selected recipes and scale factors."""

    totals: dict[tuple[str, str], float] = defaultdict(float)
    recipe_sources: dict[tuple[str, str], set[str]] = defaultdict(set)
    raw_items: dict[tuple[str, str], list[str]] = defaultdict(list)

    for selection in selections:
        if selection.scale <= 0:
            continue

        recipe = repository.get_recipe(selection.recipe_id)
        recipe_source = recipe.name
        if selection.scale != 1:
            recipe_source = f"{recipe.name} x{selection.scale:g}"

        for ingredient in recipe.ingredients:
            normalized_name = normalize_ingredient_name(ingredient.ingredient_name)
            quantity, unit = quantity_for_aggregation(
                ingredient.quantity * selection.scale,
                ingredient.unit,
            )
            key = (normalized_name, unit)
            totals[key] += quantity
            recipe_sources[key].add(recipe_source)
            raw_items[key].append(ingredient.raw_text)

    items = [
        GroceryItem(
            ingredient_name=ingredient_name,
            quantity=quantity,
            unit=unit,
            recipe_sources=tuple(sorted(recipe_sources[(ingredient_name, unit)])),
            raw_items=tuple(raw_items[(ingredient_name, unit)]),
        )
        for (ingredient_name, unit), quantity in totals.items()
    ]
    return sorted(items, key=lambda item: (item.ingredient_name, item.unit))
