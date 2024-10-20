# Project TODOs
In order:
- [x] draft all scripts
- [ ] test api credentials and ensure they're working
- [ ] start making some test recipes
    - [ ] figure out how to associate recipes with ingredients and quantities
    - [ ] do I need a recipe database? is this a class? multiple classes? etc.
        - [https://recipemd.org/](https://recipemd.org/)
        - [python recipemd data fmt](https://recipemd.org/_apidoc/recipemd.data.html)
- [ ] test adding recipes to meal list and ensure ingredients and quantities are being added properly
- [ ] scan cookbook for recipes to add
    - [ ] use gpt to codify recipes and add them to the database
- [ ] test generating grocery list with multiple recipes after adding real recipes
- [ ] start associating recipe ingredients with kroger products
- [ ] test adding items to kroger cart

# Project Ideas for optimization
- make streamlit app to serve as easy user interface for non-coders
- make sure numbers don't come out as decimals/floats, and round up to nearest whole number, then buy the smallest package that meets that quantity
    - track extra ingredients to quantify how much is left over
- create shopping report that records what was bought
- ensure a 'generic breakfast' recipe is added to the database that encompasses all regular breakfast items for us.