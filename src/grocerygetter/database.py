"""SQLite database initialization and seed loading."""

from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_DB_PATH = Path(os.getenv("GROCERYGETTER_DB", DATA_DIR / "grocerygetter.sqlite"))
SCHEMA_PATH = DATA_DIR / "schema.sql"
SEED_PATH = DATA_DIR / "seed_recipes.json"


def connect(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Open a SQLite connection with row objects and foreign keys enabled."""

    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def session(db_path: str | Path = DEFAULT_DB_PATH):
    """Yield a SQLite connection and always close it on exit."""

    connection = connect(db_path)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database(
    db_path: str | Path = DEFAULT_DB_PATH,
    *,
    seed: bool = True,
    schema_path: str | Path = SCHEMA_PATH,
    seed_path: str | Path = SEED_PATH,
) -> Path:
    """Create the database schema and load seed recipes when the DB is empty."""

    path = Path(db_path)
    with session(path) as connection:
        connection.executescript(Path(schema_path).read_text(encoding="utf-8"))
        if seed and _recipe_count(connection) == 0:
            _load_seed_recipes(connection, Path(seed_path))
    return path


def _recipe_count(connection: sqlite3.Connection) -> int:
    row = connection.execute("SELECT COUNT(*) AS count FROM recipes").fetchone()
    return int(row["count"])


def _load_seed_recipes(connection: sqlite3.Connection, seed_path: Path) -> None:
    if not seed_path.exists():
        return

    recipes: list[dict[str, Any]] = json.loads(seed_path.read_text(encoding="utf-8"))
    for recipe in recipes:
        cursor = connection.execute(
            """
            INSERT INTO recipes (name, servings, source, notes)
            VALUES (?, ?, ?, ?)
            """,
            (
                recipe["name"],
                float(recipe.get("servings", 4)),
                recipe.get("source"),
                recipe.get("notes"),
            ),
        )
        recipe_id = int(cursor.lastrowid)

        for index, ingredient in enumerate(recipe.get("ingredients", []), start=1):
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
                    ingredient.get("raw_text") or ingredient["ingredient_name"],
                    ingredient["ingredient_name"],
                    float(ingredient.get("quantity", 1)),
                    ingredient.get("unit", "each"),
                    ingredient.get("preparation"),
                ),
            )

        for index, step in enumerate(recipe.get("steps", []), start=1):
            connection.execute(
                """
                INSERT INTO recipe_steps (recipe_id, step_number, instruction)
                VALUES (?, ?, ?)
                """,
                (recipe_id, index, step),
            )
