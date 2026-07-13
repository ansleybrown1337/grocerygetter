"""Recipe import helpers for seed-style JSON payloads."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any

from .repository import RecipeRepository


@dataclass(frozen=True)
class RecipeImportSummary:
    imported: int = 0
    skipped: int = 0
    errors: tuple[str, ...] = field(default_factory=tuple)


def import_recipes_from_json(
    repository: RecipeRepository,
    payload: str | bytes,
    *,
    skip_duplicates: bool = True,
) -> RecipeImportSummary:
    """Import recipes from a JSON list or an object with a ``recipes`` list."""

    recipes = parse_recipe_json(payload)
    imported = 0
    skipped = 0
    errors: list[str] = []

    for index, recipe in enumerate(recipes, start=1):
        name = str(recipe["name"])
        try:
            repository.add_recipe(
                name=name,
                servings=float(recipe["servings"]),
                ingredients=recipe["ingredients"],
                steps=recipe["steps"],
                source=recipe["source"],
                notes=recipe["notes"],
            )
        except ValueError as exc:
            if skip_duplicates and "already exists" in str(exc):
                skipped += 1
                continue
            errors.append(f"Recipe {index} ({name}): {exc}")
        else:
            imported += 1

    return RecipeImportSummary(
        imported=imported,
        skipped=skipped,
        errors=tuple(errors),
    )


def parse_recipe_json(payload: str | bytes) -> list[dict[str, Any]]:
    """Validate and normalize recipe import JSON without writing to the database."""

    if isinstance(payload, bytes):
        payload = payload.decode("utf-8")

    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Recipe import JSON is invalid: {exc.msg}.") from exc

    if isinstance(data, dict) and "recipes" in data:
        data = data["recipes"]

    if not isinstance(data, list):
        raise ValueError("Recipe import JSON must be a recipe list or an object with a 'recipes' list.")

    recipes = []
    for index, recipe in enumerate(data, start=1):
        recipes.append(_normalize_recipe(recipe, index))
    return recipes


def _normalize_recipe(recipe: object, index: int) -> dict[str, Any]:
    if not isinstance(recipe, dict):
        raise ValueError(f"Recipe {index} must be an object.")

    name = str(recipe.get("name") or "").strip()
    if not name:
        raise ValueError(f"Recipe {index} is missing a name.")

    try:
        servings = float(recipe.get("servings", 4))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Recipe {index} ({name}) has invalid servings.") from exc
    if servings <= 0:
        raise ValueError(f"Recipe {index} ({name}) needs servings greater than zero.")

    ingredients = _normalize_ingredients(recipe.get("ingredients"), index, name)
    steps = _normalize_steps(recipe.get("steps", []), index, name)

    return {
        "name": name,
        "servings": servings,
        "source": _optional_text(recipe.get("source")),
        "notes": _optional_text(recipe.get("notes")),
        "ingredients": ingredients,
        "steps": steps,
    }


def _normalize_ingredients(value: object, recipe_index: int, recipe_name: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"Recipe {recipe_index} ({recipe_name}) needs at least one ingredient.")

    ingredients = []
    for ingredient_index, ingredient in enumerate(value, start=1):
        if not isinstance(ingredient, dict):
            raise ValueError(
                f"Recipe {recipe_index} ({recipe_name}) ingredient {ingredient_index} must be an object."
            )

        ingredient_name = str(ingredient.get("ingredient_name") or ingredient.get("name") or "").strip()
        if not ingredient_name:
            raise ValueError(
                f"Recipe {recipe_index} ({recipe_name}) ingredient {ingredient_index} is missing a name."
            )

        try:
            quantity = float(ingredient.get("quantity", 1))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Recipe {recipe_index} ({recipe_name}) ingredient {ingredient_index} has invalid quantity."
            ) from exc
        if quantity <= 0:
            raise ValueError(
                f"Recipe {recipe_index} ({recipe_name}) ingredient {ingredient_index} needs quantity greater than zero."
            )

        unit = str(ingredient.get("unit") or "each").strip() or "each"
        raw_text = str(ingredient.get("raw_text") or "").strip()
        if not raw_text:
            raw_text = f"{quantity:g} {unit} {ingredient_name}"

        ingredients.append(
            {
                "ingredient_name": ingredient_name,
                "quantity": quantity,
                "unit": unit,
                "preparation": _optional_text(ingredient.get("preparation")),
                "raw_text": raw_text,
            }
        )

    return ingredients


def _normalize_steps(value: object, recipe_index: int, recipe_name: str) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [line.strip() for line in value.splitlines() if line.strip()]
    if not isinstance(value, list):
        raise ValueError(f"Recipe {recipe_index} ({recipe_name}) steps must be a list or text block.")
    return [str(step).strip() for step in value if str(step).strip()]


def _optional_text(value: object) -> str | None:
    text = str(value or "").strip()
    return text or None
