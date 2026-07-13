from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from grocerygetter.database import initialize_database
from grocerygetter.models import ProductMapping
from grocerygetter.repository import RecipeRepository


class RecipeRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.sqlite"
        initialize_database(self.db_path, seed=False)
        self.repository = RecipeRepository(self.db_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_add_and_get_recipe(self) -> None:
        recipe_id = self.repository.add_recipe(
            name="Test Tacos",
            servings=4,
            ingredients=[
                {
                    "ingredient_name": "black beans",
                    "quantity": 2,
                    "unit": "cans",
                    "raw_text": "2 cans black beans",
                },
                {
                    "ingredient_name": "tortillas",
                    "quantity": 8,
                    "unit": "each",
                    "raw_text": "8 tortillas",
                },
            ],
            steps=["Warm beans.", "Fill tortillas."],
            source="Unit test",
        )

        recipe = self.repository.get_recipe(recipe_id)

        self.assertEqual(recipe.name, "Test Tacos")
        self.assertEqual(recipe.servings, 4)
        self.assertEqual(len(recipe.ingredients), 2)
        self.assertEqual(recipe.ingredients[0].unit, "can")
        self.assertEqual(recipe.steps, ("Warm beans.", "Fill tortillas."))

    def test_product_mapping_upsert(self) -> None:
        self.repository.upsert_product_mapping(
            ProductMapping(
                ingredient_name="Yellow Onion",
                unit="each",
                product_name="Yellow Onion",
                upc="0000000004011",
                cart_quantity=2,
            )
        )
        self.repository.upsert_product_mapping(
            ProductMapping(
                ingredient_name="yellow onion",
                unit="each",
                product_name="Kroger Yellow Onion",
                upc="0001111094011",
                cart_quantity=1,
            )
        )

        mappings = self.repository.list_product_mappings()
        mapping = self.repository.get_product_mapping("yellow onion", "each")

        self.assertEqual(len(mappings), 1)
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.product_name, "Kroger Yellow Onion")
        self.assertEqual(mapping.upc, "0001111094011")
        self.assertEqual(mapping.cart_quantity, 1)


if __name__ == "__main__":
    unittest.main()
