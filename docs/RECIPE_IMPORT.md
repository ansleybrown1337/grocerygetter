# Recipe Import Format

GroceryGetter can import recipes from a JSON file in the Recipes tab of the Streamlit app. Use this when you want to add several recipes at once instead of entering them manually.

For a complete working example, see [`data/seed_recipes.json`](../data/seed_recipes.json).

## How To Import

1. Start the app:

   ```bash
   streamlit run app.py
   ```

2. Open the **Recipes** tab.
3. In **Import Recipes**, choose a `.json` file.
4. Keep **Skip duplicate recipe names** checked if you want existing recipes to be ignored instead of reported as errors.
5. Select **Import Recipes**.

Imported recipes are saved directly into the SQLite database configured by `GROCERYGETTER_DB`, or `data/grocerygetter.sqlite` by default.

## File Shape

The file can be either a top-level JSON array:

```json
[
  {
    "name": "Black Bean Tacos",
    "servings": 4,
    "source": "Family cookbook",
    "notes": "Optional notes",
    "ingredients": [
      {
        "raw_text": "2 cans black beans",
        "ingredient_name": "black beans",
        "quantity": 2,
        "unit": "can",
        "preparation": null
      }
    ],
    "steps": ["Warm beans.", "Fill tortillas."]
  }
]
```

Or an object with a top-level `recipes` array:

```json
{
  "recipes": [
    {
      "name": "Tomato Basil Pasta",
      "servings": 4,
      "ingredients": [
        {
          "ingredient_name": "pasta",
          "quantity": 12,
          "unit": "oz"
        }
      ],
      "steps": "Boil pasta until al dente.\nToss with sauce."
    }
  ]
}
```

## Recipe Fields

Required:

- `name`: Recipe name. It must be unique in the database.
- `ingredients`: Non-empty list of ingredient objects.

Optional:

- `servings`: Number of servings. Defaults to `4`.
- `source`: Cookbook, URL, person, or other source note.
- `notes`: Extra recipe notes.
- `steps`: Either a list of step strings or a single text block with one step per line.

## Ingredient Fields

Required:

- `ingredient_name`: Grocery item name. You can also use `name` as a shorthand.

Optional:

- `quantity`: Numeric amount. Defaults to `1`.
- `unit`: Unit such as `each`, `cup`, `tbsp`, `oz`, or `lb`. Defaults to `each`.
- `raw_text`: Original ingredient text. If omitted, GroceryGetter creates one from quantity, unit, and name.
- `preparation`: Prep note such as `diced`, `minced`, or `sliced`.

## Notes

- Common units are normalized during import, so `cups` becomes `cup` and `cans` becomes `can`.
- Unknown units are preserved as entered.
- Duplicate recipe names are skipped when **Skip duplicate recipe names** is checked.
- If one recipe has invalid data, the app reports that recipe and continues importing the rest of the file.
