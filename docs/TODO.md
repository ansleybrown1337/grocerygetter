# Project TODOs

## Done

- [x] Draft original prototype scripts.
- [x] Move recipe storage toward data instead of per-recipe classes.
- [x] Add SQLite schema for recipes, ingredients, steps, and product mappings.
- [x] Add seed recipes for local testing.
- [x] Add grocery-list aggregation tests.
- [x] Add Streamlit MVP workflow.

## Next

- [ ] Add recipe editing and deletion in the UI.
- [ ] Improve ingredient parsing beyond the current pipe-delimited input.
- [ ] Add import/export tools for JSON seed data.
- [ ] Test Kroger API credentials.
- [ ] Implement OAuth callback handling for shopper-authorized Kroger tokens.
- [ ] Add Kroger location search.
- [ ] Add Kroger product search for each grocery item.
- [ ] Let users choose preferred Kroger products and save UPC mappings.
- [ ] Convert recipe quantities into package counts.
- [ ] Enable reviewed add-to-cart calls.

## Later Ideas

- [ ] Scan cookbook recipes and codify them into seed/import data.
- [ ] Track leftover ingredients after package-size conversion.
- [ ] Create shopping reports for what was bought.
- [ ] Add a reusable breakfast template recipe.
- [ ] Move from Streamlit to a responsive web frontend if the app outgrows the prototype UI.
