"""
grocerygetter.py
Created by AJ Brown
ansleybrown1337@gmail.com
20 Oct 2024

Remember to update the environment.yml and requirements.txt files with any new libraries
used in this file. 
For conda, use the following command:
conda env export --no-builds > environment.yml
For pip, use the following command:
pip freeze > requirements.txt
"""

from auth import get_access_token, refresh_access_token
from recipes import create_recipe, list_recipes, generate_grocery_list
from kroger_api import search_product, add_to_cart

def main():
    print("Welcome to GroceryGetter!")
    
    # Step 1: Authenticate the user
    access_token = get_access_token()
    if not access_token:
        print("Failed to get access token.")
        return

    # Step 2: Handle recipe management
    print("1. Create a new recipe")
    print("2. View existing recipes")
    choice = input("Choose an option (1 or 2): ")
    
    if choice == '1':
        name = input("Enter recipe name: ")
        ingredients = input("Enter ingredients (comma separated): ").split(',')
        create_recipe(name, ingredients)
    
    recipes = list_recipes()
    print(f"Available recipes: {recipes}")
    
    # Step 3: Generate a grocery list from selected recipes
    meal_list = input("Select recipes to add to your meal list (comma separated): ").split(',')
    grocery_list = generate_grocery_list(meal_list)
    print(f"Grocery list: {grocery_list}")
    
    # Step 4: Add items to Kroger cart
    for item in grocery_list:
        product_id = search_product(item)
        if product_id:
            add_to_cart(product_id, 1)  # Add 1 of each item
    
    print("Items added to your Kroger cart!")

if __name__ == "__main__":
    main()
