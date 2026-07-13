"""Repository layer for SQLite-backed recipe and product preference data."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from .database import DEFAULT_DB_PATH, session
from .models import ProductMapping, Recipe, RecipeIngredient, RecipeSummary
from .units import normalize_ingredient_name, normalize_unit


class RecipeRepository:
    """Small SQLite repository used by the CLI/tests/Streamlit UI."""

    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)

    def count_recipes(self) -> int:
        with session(self.db_path) as connection:
            row = connection.execute("SELECT COUNT(*) AS count FROM recipes").fetchone()
            return int(row["count"])

    def list_recipe_summaries(self) -> list[RecipeSummary]:
        with session(self.db_path) as connection:
            rows = connection.execute(
                """
                SELECT id, name, servings, source
                FROM recipes
                ORDER BY name
                """
            ).fetchall()
        return [
            RecipeSummary(
                id=int(row["id"]),
                name=str(row["name"]),
                servings=float(row["servings"]),
                source=row["source"],
            )
            for row in rows
        ]

    def list_known_ingredients(self) -> list[str]:
        with session(self.db_path) as connection:
            rows = connection.execute(
                """
                SELECT DISTINCT LOWER(TRIM(ingredient_name)) AS ingredient_name
                FROM recipe_ingredients
                WHERE TRIM(ingredient_name) != ''
                ORDER BY ingredient_name
                """
            ).fetchall()
        return [str(row["ingredient_name"]) for row in rows]

    def get_recipe(self, recipe_id: int) -> Recipe:
        with session(self.db_path) as connection:
            recipe_row = connection.execute(
                """
                SELECT id, name, servings, source, notes
                FROM recipes
                WHERE id = ?
                """,
                (recipe_id,),
            ).fetchone()
            if recipe_row is None:
                raise KeyError(f"Recipe id {recipe_id} was not found")

            ingredient_rows = connection.execute(
                """
                SELECT id, recipe_id, raw_text, ingredient_name, quantity, unit, preparation, sort_order
                FROM recipe_ingredients
                WHERE recipe_id = ?
                ORDER BY sort_order, id
                """,
                (recipe_id,),
            ).fetchall()

            step_rows = connection.execute(
                """
                SELECT instruction
                FROM recipe_steps
                WHERE recipe_id = ?
                ORDER BY step_number, id
                """,
                (recipe_id,),
            ).fetchall()

        ingredients = tuple(
            RecipeIngredient(
                id=int(row["id"]),
                recipe_id=int(row["recipe_id"]),
                raw_text=str(row["raw_text"]),
                ingredient_name=str(row["ingredient_name"]),
                quantity=float(row["quantity"]),
                unit=str(row["unit"]),
                preparation=row["preparation"],
                sort_order=int(row["sort_order"]),
            )
            for row in ingredient_rows
        )
        steps = tuple(str(row["instruction"]) for row in step_rows)

        return Recipe(
            id=int(recipe_row["id"]),
            name=str(recipe_row["name"]),
            servings=float(recipe_row["servings"]),
            source=recipe_row["source"],
            notes=recipe_row["notes"],
            ingredients=ingredients,
            steps=steps,
        )

    def add_recipe(
        self,
        *,
        name: str,
        servings: float,
        ingredients: Iterable[dict[str, object]],
        steps: Iterable[str] = (),
        source: str | None = None,
        notes: str | None = None,
    ) -> int:
        with session(self.db_path) as connection:
            try:
                cursor = connection.execute(
                    """
                    INSERT INTO recipes (name, servings, source, notes)
                    VALUES (?, ?, ?, ?)
                    """,
                    (name.strip(), float(servings), source, notes),
                )
            except sqlite3.IntegrityError as exc:
                raise ValueError(f"Recipe '{name}' already exists") from exc

            recipe_id = int(cursor.lastrowid)
            for index, ingredient in enumerate(ingredients, start=1):
                ingredient_name = str(ingredient["ingredient_name"]).strip()
                raw_text = str(ingredient.get("raw_text") or ingredient_name)
                unit = normalize_unit(str(ingredient.get("unit") or "each"))
                connection.execute(
                    """
                    INSERT INTO recipe_ingredients (
                        recipe_id,
                        sort_order,
                        raw_text,
                        ingredient_name,
                        quantity,
                        unit,
                        preparation
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        recipe_id,
                        index,
                        raw_text,
                        ingredient_name,
                        float(ingredient.get("quantity", 1)),
                        unit,
                        ingredient.get("preparation"),
                    ),
                )

            for index, step in enumerate(steps, start=1):
                if str(step).strip():
                    connection.execute(
                        """
                        INSERT INTO recipe_steps (recipe_id, step_number, instruction)
                        VALUES (?, ?, ?)
                        """,
                        (recipe_id, index, str(step).strip()),
                    )

        return recipe_id

    def list_product_mappings(self) -> list[ProductMapping]:
        with session(self.db_path) as connection:
            rows = connection.execute(
                """
                SELECT ingredient_name, unit, product_name, upc, cart_quantity, brand, package_size, location_id, modality
                FROM product_mappings
                ORDER BY ingredient_name, unit, location_id, modality
                """
            ).fetchall()
        return [_mapping_from_row(row) for row in rows]

    def get_product_mapping(
        self,
        ingredient_name: str,
        unit: str,
        *,
        location_id: str = "",
        modality: str = "PICKUP",
    ) -> ProductMapping | None:
        with session(self.db_path) as connection:
            row = connection.execute(
                """
                SELECT ingredient_name, unit, product_name, upc, cart_quantity, brand, package_size, location_id, modality
                FROM product_mappings
                WHERE ingredient_name = ?
                  AND unit = ?
                  AND location_id = ?
                  AND modality = ?
                """,
                (
                    normalize_ingredient_name(ingredient_name),
                    normalize_unit(unit),
                    location_id,
                    modality,
                ),
            ).fetchone()
        return _mapping_from_row(row) if row is not None else None

    def upsert_product_mapping(self, mapping: ProductMapping) -> None:
        with session(self.db_path) as connection:
            connection.execute(
                """
                INSERT INTO product_mappings (
                    ingredient_name,
                    unit,
                    product_name,
                    upc,
                    cart_quantity,
                    brand,
                    package_size,
                    location_id,
                    modality,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(ingredient_name, unit, location_id, modality)
                DO UPDATE SET
                    product_name = excluded.product_name,
                    upc = excluded.upc,
                    cart_quantity = excluded.cart_quantity,
                    brand = excluded.brand,
                    package_size = excluded.package_size,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    normalize_ingredient_name(mapping.ingredient_name),
                    normalize_unit(mapping.unit),
                    mapping.product_name.strip(),
                    mapping.upc.strip(),
                    int(mapping.cart_quantity),
                    mapping.brand,
                    mapping.package_size,
                    mapping.location_id,
                    mapping.modality,
                ),
            )


def _mapping_from_row(row: sqlite3.Row) -> ProductMapping:
    return ProductMapping(
        ingredient_name=str(row["ingredient_name"]),
        unit=str(row["unit"]),
        product_name=str(row["product_name"]),
        upc=str(row["upc"]),
        cart_quantity=int(row["cart_quantity"]),
        brand=row["brand"],
        package_size=row["package_size"],
        location_id=str(row["location_id"]),
        modality=str(row["modality"]),
    )
