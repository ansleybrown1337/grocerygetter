from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from grocerygetter.database import initialize_database
from grocerygetter.kroger import build_cart_payload
from grocerygetter.meal_planner import build_grocery_list
from grocerygetter.models import MealSelection, ProductMapping
from grocerygetter.repository import RecipeRepository


class MealPlannerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.sqlite"
        initialize_database(self.db_path, seed=False)
        self.repository = RecipeRepository(self.db_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_build_grocery_list_combines_matching_ingredients_and_units(self) -> None:
        first_id = self.repository.add_recipe(
            name="First Recipe",
            servings=4,
            ingredients=[
                {"ingredient_name": "yellow onion", "quantity": 1, "unit": "each"},
                {"ingredient_name": "olive oil", "quantity": 1, "unit": "tbsp"},
            ],
        )
        second_id = self.repository.add_recipe(
            name="Second Recipe",
            servings=2,
            ingredients=[
                {"ingredient_name": "Yellow Onion", "quantity": 2, "unit": "each"},
                {"ingredient_name": "olive oil", "quantity": 3, "unit": "tsp"},
            ],
        )

        grocery_items = build_grocery_list(
            self.repository,
            [
                MealSelection(first_id, scale=1),
                MealSelection(second_id, scale=2),
            ],
        )
        by_key = {(item.ingredient_name, item.unit): item for item in grocery_items}

        self.assertEqual(by_key[("yellow onion", "each")].quantity, 5)
        self.assertAlmostEqual(by_key[("olive oil", "cup")].quantity, 0.1875)
        self.assertEqual(
            by_key[("yellow onion", "each")].recipe_sources,
            ("First Recipe", "Second Recipe x2"),
        )

    def test_build_cart_payload_uses_saved_mappings(self) -> None:
        recipe_id = self.repository.add_recipe(
            name="Mapped Recipe",
            servings=1,
            ingredients=[
                {"ingredient_name": "yellow onion", "quantity": 1, "unit": "each"},
                {"ingredient_name": "garlic", "quantity": 2, "unit": "clove"},
            ],
        )
        grocery_items = build_grocery_list(self.repository, [MealSelection(recipe_id)])
        mappings = {
            ("yellow onion", "each"): ProductMapping(
                ingredient_name="yellow onion",
                unit="each",
                product_name="Yellow Onion",
                upc="0000000004011",
                cart_quantity=2,
            )
        }

        payload = build_cart_payload(grocery_items, mappings)

        self.assertEqual(
            payload,
            {
                "items": [
                    {
                        "upc": "0000000004011",
                        "quantity": 2,
                        "modality": "PICKUP",
                    }
                ]
            },
        )


if __name__ == "__main__":
    unittest.main()
