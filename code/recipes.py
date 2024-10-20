# /recipes.py

# Example: Storing recipes in memory for simplicity
recipes = []

# Create a new recipe
def create_recipe(name, ingredients):
    recipe = {"name": name, "ingredients": ingredients}
    recipes.append(recipe)
    print(f"Recipe '{name}' created with ingredients: {ingredients}")

# List all available recipes
def list_recipes():
    return [recipe['name'] for recipe in recipes]

# Generate grocery list from selected meal list
def generate_grocery_list(meal_list):
    grocery_list = []
    for meal in meal_list:
        for recipe in recipes:
            if recipe['name'] == meal:
                grocery_list.extend(recipe['ingredients'])
    return grocery_list
