"""Streamlit entrypoint for GroceryGetter."""

from __future__ import annotations

import base64
from difflib import get_close_matches
import sys
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent
SRC_ROOT = APP_ROOT / "src"
BANNER_PATH = APP_ROOT / "figs" / "grocerygetter-banner.png"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import streamlit as st

from grocerygetter.database import DEFAULT_DB_PATH, initialize_database
from grocerygetter.kroger import build_cart_payload
from grocerygetter.meal_planner import build_grocery_list
from grocerygetter.models import GroceryItem, MealSelection, ProductMapping
from grocerygetter.repository import RecipeRepository
from grocerygetter.units import format_quantity, normalize_ingredient_name, normalize_unit

AUTHOR_NAME = "AJ Brown"
AUTHOR_GITHUB_URL = "https://github.com/ansleybrown1337"
MAKE_GROCERY_LIST_VIEW = "Make Grocery List"
REVIEW_CART_VIEW = "Review Cart & Order"
CONFIGURATION_VIEW = "Configuration"
VENDOR_STATUS = {
    "Kroger": "Available soon",
    "Target": "In progress",
    "Walmart": "In progress",
}


def main() -> None:
    st.set_page_config(page_title="GroceryGetter", page_icon="GG", layout="wide")
    apply_brand_styles()

    db_path = initialize_database(DEFAULT_DB_PATH)
    repository = RecipeRepository(db_path)

    render_brand_header()

    active_view = render_navigation(
        ["How To Use", MAKE_GROCERY_LIST_VIEW, REVIEW_CART_VIEW, "Recipes", CONFIGURATION_VIEW]
    )

    if active_view == "How To Use":
        render_how_to_tab()
    elif active_view == MAKE_GROCERY_LIST_VIEW:
        render_make_grocery_list_tab(repository)
    elif active_view == REVIEW_CART_VIEW:
        render_review_cart_tab(repository)
    elif active_view == "Recipes":
        render_recipes_tab(repository)
    elif active_view == CONFIGURATION_VIEW:
        render_configuration_tab(repository)


def apply_brand_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --gg-bg: #fffdf8;
                --gg-surface: #fbf7f2;
                --gg-surface-strong: #fff1e9;
                --gg-ink: #243235;
                --gg-muted: #627375;
                --gg-teal: #2d6f88;
                --gg-teal-dark: #214f63;
                --gg-salmon: #d9786f;
                --gg-salmon-dark: #b95c54;
                --gg-sky: #d8ecf7;
                --gg-mint: #dff2e6;
                --gg-peach: #ffe2d2;
                --gg-cream: #fff4df;
                --gg-border: #eadfd4;
            }

            .stApp {
                background:
                    radial-gradient(circle at 12% 8%, rgba(255, 226, 210, 0.78), transparent 28rem),
                    radial-gradient(circle at 92% 10%, rgba(216, 236, 247, 0.7), transparent 24rem),
                    linear-gradient(180deg, #fffdf8 0%, #fbf7f2 100%);
                color: var(--gg-ink);
            }

            .block-container {
                padding-top: 2rem;
                padding-bottom: 4rem;
                max-width: 1180px;
            }

            .gg-brand-header {
                padding: 1.25rem 0 1.6rem;
                border-bottom: 1px solid rgba(217, 120, 111, 0.26);
                margin-bottom: 1.35rem;
            }

            .gg-banner {
                border: 1px solid rgba(234, 223, 212, 0.85);
                border-radius: 8px;
                box-shadow: 0 16px 36px rgba(36, 50, 53, 0.08);
                margin-bottom: 1.15rem;
                overflow: hidden;
                position: relative;
            }

            .gg-banner img {
                display: block;
                width: 100%;
                max-height: 280px;
                object-fit: cover;
                object-position: center;
            }

            .gg-banner-title {
                color: var(--gg-ink);
                font-size: clamp(3.1rem, 7.5vw, 6.4rem);
                font-weight: 850;
                left: clamp(4.5rem, 16vw, 13rem);
                line-height: 0.95;
                margin: 0;
                position: absolute;
                text-shadow: 0 2px 18px rgba(255, 253, 248, 0.92);
                top: 50%;
                transform: translateY(-50%);
                white-space: nowrap;
            }

            .gg-banner-title span {
                color: var(--gg-salmon-dark);
            }

            .gg-kicker {
                color: var(--gg-salmon-dark);
                font-size: 0.86rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin-bottom: 0.35rem;
            }

            .gg-title {
                color: var(--gg-ink);
                font-size: clamp(2.3rem, 5vw, 4.2rem);
                font-weight: 800;
                line-height: 1;
                margin: 0;
            }

            .gg-subtitle {
                color: var(--gg-muted);
                font-size: 1.05rem;
                line-height: 1.55;
                max-width: 760px;
                margin: 0.8rem 0 0;
            }

            .gg-author {
                color: var(--gg-muted);
                font-size: 0.95rem;
                margin-top: 0.8rem;
            }

            .gg-author a {
                color: var(--gg-teal-dark);
                font-weight: 700;
                text-decoration: none;
                border-bottom: 2px solid rgba(217, 120, 111, 0.65);
            }

            .gg-author a:hover {
                color: #194345;
                border-bottom-color: var(--gg-salmon-dark);
            }

            h2, h3 {
                color: var(--gg-ink);
            }

            div[data-testid="stTabs"] button {
                color: var(--gg-muted);
                font-weight: 650;
            }

            div[data-testid="stTabs"] button[aria-selected="true"] {
                color: var(--gg-teal-dark);
            }

            div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
                background-color: var(--gg-salmon);
            }

            div[role="radiogroup"] {
                gap: 0.35rem;
                margin-bottom: 1rem;
            }

            div[role="radiogroup"] label {
                background: rgba(255, 253, 248, 0.78);
                border: 1px solid var(--gg-border);
                border-radius: 8px;
                padding: 0.35rem 0.65rem;
            }

            div[role="radiogroup"] label:has(input:checked) {
                background: var(--gg-surface-strong);
                border-color: rgba(217, 120, 111, 0.55);
                color: var(--gg-salmon-dark);
                font-weight: 700;
            }

            div[data-testid="stDataFrame"],
            div[data-testid="stDataEditor"] {
                border: 1px solid var(--gg-border);
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 10px 28px rgba(36, 50, 53, 0.06);
            }

            div[data-testid="stForm"] {
                background: rgba(255, 253, 248, 0.88);
                border: 1px solid var(--gg-border);
                border-radius: 8px;
                padding: 1rem;
                box-shadow: 0 10px 28px rgba(36, 50, 53, 0.05);
            }

            .stButton > button,
            .stFormSubmitButton > button {
                border-radius: 8px;
                border: 1px solid var(--gg-salmon);
                background: var(--gg-salmon);
                color: #ffffff;
                font-weight: 700;
                box-shadow: 0 6px 16px rgba(185, 92, 84, 0.2);
            }

            .stButton > button[kind="secondary"],
            .stFormSubmitButton > button[kind="secondary"] {
                background: rgba(255, 253, 248, 0.82);
                border-color: var(--gg-border);
                color: var(--gg-muted);
                box-shadow: none;
            }

            .stButton > button:hover,
            .stFormSubmitButton > button:hover {
                border-color: var(--gg-salmon-dark);
                background: var(--gg-salmon-dark);
                color: #ffffff;
            }

            .stButton > button:disabled {
                background: #e0e8e6;
                border-color: #d0dcda;
                color: #6f7f81;
                box-shadow: none;
            }

            div[data-testid="stAlert"] {
                border-radius: 8px;
                border: 1px solid var(--gg-border);
            }

            code {
                color: var(--gg-teal-dark);
                background: #fff1e9;
                border-radius: 4px;
                padding: 0.12rem 0.25rem;
            }

            .gg-workflow {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 0.8rem;
                margin: 1rem 0 1.5rem;
            }

            .gg-workflow-step {
                background: rgba(255, 253, 248, 0.86);
                border: 1px solid var(--gg-border);
                border-left: 5px solid var(--gg-salmon);
                border-radius: 8px;
                padding: 0.95rem;
                box-shadow: 0 8px 20px rgba(36, 50, 53, 0.05);
            }

            .gg-workflow-step strong {
                display: block;
                color: var(--gg-ink);
                margin-bottom: 0.25rem;
            }

            .gg-workflow-step span {
                color: var(--gg-muted);
                font-size: 0.94rem;
                line-height: 1.45;
            }

            .gg-help-list li {
                margin-bottom: 0.45rem;
            }

            @media (max-width: 760px) {
                .block-container {
                    padding: 1rem 0.85rem 3rem;
                }

                .gg-brand-header {
                    padding-top: 0.75rem;
                    margin-bottom: 1rem;
                }

                .gg-banner img {
                    max-height: 170px;
                    object-position: 62% center;
                }

                .gg-banner-title {
                    font-size: 2.45rem;
                    left: 1.25rem;
                    top: 38%;
                }

                .gg-title {
                    font-size: 2.35rem;
                }

                .gg-subtitle {
                    font-size: 0.98rem;
                }

                .gg-workflow {
                    grid-template-columns: 1fr;
                }

                div[data-testid="column"] {
                    width: 100% !important;
                    flex: 1 1 100% !important;
                }

                div[data-testid="stHorizontalBlock"] {
                    gap: 0.35rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_brand_header() -> None:
    if BANNER_PATH.exists():
        st.markdown(
            f"""
            <div class="gg-banner">
                <img src="{image_data_uri(BANNER_PATH)}" alt="Illustrated groceries and produce banner" />
                <h1 class="gg-banner-title">Grocery<span>Getter</span></h1>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <header class="gg-brand-header">
            <div class="gg-kicker">Meal planning to grocery cart</div>
            <p class="gg-subtitle">
                Plan recipes, combine ingredients, and prepare a reviewed grocery cart
                without rebuilding the same shopping list every week.
            </p>
            <p class="gg-author">
                Created by <a href="{AUTHOR_GITHUB_URL}" target="_blank" rel="noopener noreferrer">{AUTHOR_NAME}</a>
            </p>
        </header>
        """,
        unsafe_allow_html=True,
    )


def image_data_uri(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def render_navigation(options: list[str]) -> str:
    if "active_view" not in st.session_state:
        st.session_state.active_view = options[0]

    columns = st.columns(len(options))
    for option, column in zip(options, columns):
        with column:
            is_active = st.session_state.active_view == option
            if st.button(
                option,
                key=f"nav-{option}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                st.session_state.active_view = option

    return str(st.session_state.active_view)


def render_how_to_tab() -> None:
    st.subheader("How To Use")
    st.markdown(
        """
        <div class="gg-workflow">
            <div class="gg-workflow-step">
                <strong>1. Make grocery list</strong>
                <span>Select recipes, scale them, and edit the combined grocery draft.</span>
            </div>
            <div class="gg-workflow-step">
                <strong>2. Review cart</strong>
                <span>Choose vendor preferences and map groceries to products.</span>
            </div>
            <div class="gg-workflow-step">
                <strong>3. Order</strong>
                <span>Send reviewed items to a cart when vendor integrations are ready.</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <ul class="gg-help-list">
            <li>Use <strong>Make Grocery List</strong> to choose recipes and edit the grocery draft.</li>
            <li>Use <strong>Review Cart & Order</strong> to choose a vendor, map products, and prepare the order.</li>
            <li>Use <strong>Recipes</strong> to browse the library or add new recipes.</li>
            <li>Use <strong>Configuration</strong> to review saved product choices and future vendor connections.</li>
        </ul>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Get Started", type="primary"):
        st.session_state.active_view = MAKE_GROCERY_LIST_VIEW
        st.rerun()

    st.subheader("About")
    st.write(
        "GroceryGetter is a local recipe planning tool that stores recipes in SQLite, "
        "aggregates ingredients into a grocery list, and prepares the workflow for reviewed "
        "grocery cart automation. Live vendor cart writes are intentionally disabled until "
        "authentication, product search, and user review are fully wired in."
    )


def render_make_grocery_list_tab(repository: RecipeRepository) -> None:
    summaries = repository.list_recipe_summaries()
    recipe_options = {recipe.name: recipe for recipe in summaries}

    st.subheader("Make Grocery List")
    hydrate_grocery_list_widget_state(recipe_options)
    selected_names = st.multiselect(
        "Recipes",
        options=list(recipe_options.keys()),
        key="selected_recipe_names_widget",
    )
    st.session_state.selected_recipe_names_persisted = selected_names

    selections: list[MealSelection] = []
    if selected_names:
        columns = st.columns(min(3, len(selected_names)))
        for index, recipe_name in enumerate(selected_names):
            recipe = recipe_options[recipe_name]
            with columns[index % len(columns)]:
                scale_widget_key = f"scale-widget-{recipe.id}"
                scale = st.number_input(
                    f"{recipe.name} multiplier",
                    min_value=0.25,
                    max_value=12.0,
                    step=0.25,
                    key=scale_widget_key,
                )
            st.session_state.recipe_scale_values[recipe.id] = scale
            selections.append(MealSelection(recipe_id=recipe.id, scale=scale))

    grocery_items = build_grocery_list(repository, selections) if selections else []

    st.subheader("Review Grocery Draft")
    if not grocery_items:
        st.info("Select at least one recipe to generate a grocery list.")
        return

    ensure_cart_draft(grocery_items)
    edited_rows = st.data_editor(
        st.session_state.cart_draft,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Include": st.column_config.CheckboxColumn(
                "Include",
                help="Uncheck pantry items you already have.",
            ),
            "Quantity": st.column_config.NumberColumn(min_value=0.0, step=0.25),
        },
        disabled=["Ingredient", "Unit", "Recipes"],
        key="grocery-draft-editor",
    )
    st.session_state.cart_draft = normalize_cart_draft_rows(edited_rows)

    included_count = len(get_included_cart_rows())
    st.caption(f"{included_count} item(s) will carry forward to cart review.")
    if st.button("Review Cart & Order", type="primary"):
        st.session_state.active_view = REVIEW_CART_VIEW
        st.rerun()


def hydrate_grocery_list_widget_state(recipe_options: dict[str, object]) -> None:
    if "selected_recipe_names_persisted" not in st.session_state:
        st.session_state.selected_recipe_names_persisted = list(
            st.session_state.get("selected_recipe_names", [])
        )

    valid_names = [
        name
        for name in st.session_state.selected_recipe_names_persisted
        if name in recipe_options
    ]
    st.session_state.selected_recipe_names_persisted = valid_names

    if "selected_recipe_names_widget" not in st.session_state:
        st.session_state.selected_recipe_names_widget = valid_names

    if "recipe_scale_values" not in st.session_state:
        st.session_state.recipe_scale_values = {}

    for recipe in recipe_options.values():
        scale_widget_key = f"scale-widget-{recipe.id}"
        legacy_scale_key = f"scale-{recipe.id}"
        saved_scale = st.session_state.recipe_scale_values.get(
            recipe.id,
            st.session_state.get(legacy_scale_key, 1.0),
        )
        st.session_state.recipe_scale_values[recipe.id] = float(saved_scale)
        if scale_widget_key not in st.session_state:
            st.session_state[scale_widget_key] = float(saved_scale)


def render_review_cart_tab(repository: RecipeRepository) -> None:
    st.subheader("Review Cart & Order")
    if st.button("Back To Grocery List"):
        st.session_state.active_view = MAKE_GROCERY_LIST_VIEW
        st.rerun()

    cart_rows = get_orderable_cart_rows()
    if not cart_rows:
        st.info("Make a grocery list first, then return here to review vendor products.")
        if st.button("Make Grocery List", type="primary"):
            st.session_state.active_view = MAKE_GROCERY_LIST_VIEW
            st.rerun()
        return

    vendor_label = st.selectbox(
        "Vendor",
        options=[vendor_option_label(name) for name in VENDOR_STATUS],
        help="Kroger is the first planned live integration. Other vendors are shown to demonstrate the future multi-vendor flow.",
    )
    vendor = vendor_label.split(" - ", 1)[0]
    if vendor != "Kroger":
        st.info(f"{vendor} ordering is not available yet. This placeholder shows where future vendor integrations will fit.")

    default_modality = st.selectbox(
        "Fulfillment",
        options=["PICKUP", "DELIVERY"],
        help="Pickup and delivery are represented now; each vendor integration can translate this later.",
    )

    st.markdown("**Cart Review**")
    st.caption(
        "This page is where grocery-list items become vendor products. For now, product matching can be entered manually; vendor search comes next."
    )
    edited_rows = st.data_editor(
        build_product_review_rows(repository, cart_rows, vendor, default_modality),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Include": st.column_config.CheckboxColumn(
                "Include",
                help="Uncheck items you do not want to order.",
            ),
            "Cart quantity": st.column_config.NumberColumn(min_value=1, step=1),
            "Modality": st.column_config.SelectboxColumn(options=["PICKUP", "DELIVERY"]),
        },
        disabled=["Ingredient", "Unit", "Needed", "Recipes", "Vendor"],
        key=f"cart-mapping-editor-{vendor}",
    )
    update_cart_draft_include_from_review(edited_rows)
    orderable_rows = get_included_cart_rows()
    if not orderable_rows:
        st.warning("All cart items are currently unchecked. Re-check at least one item before ordering.")

    if st.button("Save Product Preferences", type="primary"):
        saved = 0
        for row in iter_table_rows(edited_rows):
            product_name = str(row.get("Product name") or "").strip()
            upc = str(row.get("UPC") or "").strip()
            if not product_name or not upc:
                continue
            repository.upsert_product_mapping(
                ProductMapping(
                    ingredient_name=normalize_ingredient_name(str(row["Ingredient"])),
                    unit=normalize_unit(str(row["Unit"])),
                    product_name=product_name,
                    upc=upc,
                    cart_quantity=int(row.get("Cart quantity") or 1),
                    modality=str(row.get("Modality") or "PICKUP"),
                )
            )
            saved += 1
        st.success(f"Saved {saved} product mapping(s).")
        st.rerun()

    mappings = mappings_from_product_review_rows(edited_rows)
    payload = build_cart_payload(cart_rows_to_grocery_items(orderable_rows), mappings)

    with st.expander("Advanced: cart payload preview", expanded=False):
        st.json(payload)
    unmapped_count = len(orderable_rows) - len(payload["items"])
    add_disabled = unmapped_count > 0
    help_text = (
        f"{unmapped_count} grocery item(s) still need saved product mappings."
        if add_disabled
        else f"Live {vendor} cart writes will be enabled after OAuth is wired into the new app."
    )
    st.button(f"Add To {vendor} Cart", disabled=True, help=help_text)


def ensure_cart_draft(grocery_items: list[GroceryItem]) -> None:
    fingerprint = grocery_items_fingerprint(grocery_items)
    if st.session_state.get("cart_source_fingerprint") == fingerprint:
        return

    st.session_state.cart_source_fingerprint = fingerprint
    st.session_state.cart_draft = [
        {
            "Include": True,
            "Ingredient": item.ingredient_name,
            "Quantity": item.quantity,
            "Unit": item.unit,
            "Recipes": ", ".join(item.recipe_sources),
        }
        for item in grocery_items
    ]


def grocery_items_fingerprint(grocery_items: list[GroceryItem]) -> str:
    return repr(
        [
            (
                item.ingredient_name,
                round(item.quantity, 6),
                item.unit,
                tuple(item.recipe_sources),
            )
            for item in grocery_items
        ]
    )


def normalize_cart_draft_rows(rows: object) -> list[dict[str, object]]:
    normalized_rows = []
    for row in iter_table_rows(rows):
        ingredient = normalize_ingredient_name(str(row.get("Ingredient", "")))
        if not ingredient:
            continue
        normalized_rows.append(
            {
                "Include": bool(row.get("Include", True)),
                "Ingredient": ingredient,
                "Quantity": float(row.get("Quantity") or 0),
                "Unit": normalize_unit(str(row.get("Unit", "each"))),
                "Recipes": str(row.get("Recipes", "")),
            }
        )
    return normalized_rows


def get_included_cart_rows() -> list[dict[str, object]]:
    return [
        row
        for row in st.session_state.get("cart_draft", [])
        if bool(row.get("Include", True)) and float(row.get("Quantity") or 0) > 0
    ]


def get_orderable_cart_rows() -> list[dict[str, object]]:
    return [
        row
        for row in st.session_state.get("cart_draft", [])
        if float(row.get("Quantity") or 0) > 0
    ]


def update_cart_draft_include_from_review(rows: object) -> None:
    include_by_key = {
        (
            normalize_ingredient_name(str(row.get("Ingredient", ""))),
            normalize_unit(str(row.get("Unit", "each"))),
        ): bool(row.get("Include", True))
        for row in iter_table_rows(rows)
    }

    updated_rows = []
    for row in st.session_state.get("cart_draft", []):
        key = (
            normalize_ingredient_name(str(row.get("Ingredient", ""))),
            normalize_unit(str(row.get("Unit", "each"))),
        )
        if key in include_by_key:
            row = dict(row)
            row["Include"] = include_by_key[key]
        updated_rows.append(row)
    st.session_state.cart_draft = updated_rows


def vendor_option_label(vendor: str) -> str:
    return f"{vendor} - {VENDOR_STATUS[vendor]}"


def build_product_review_rows(
    repository: RecipeRepository,
    cart_rows: list[dict[str, object]],
    vendor: str,
    default_modality: str,
) -> list[dict[str, object]]:
    review_rows = []
    for row in cart_rows:
        ingredient = str(row["Ingredient"])
        unit = str(row["Unit"])
        mapping = repository.get_product_mapping(ingredient, unit, modality=default_modality)
        review_rows.append(
            {
                "Include": bool(row.get("Include", True)),
                "Vendor": vendor,
                "Ingredient": ingredient,
                "Needed": format_quantity(float(row["Quantity"])),
                "Unit": unit,
                "Recipes": str(row.get("Recipes", "")),
                "Product name": mapping.product_name if mapping else "",
                "UPC": mapping.upc if mapping else "",
                "Cart quantity": mapping.cart_quantity if mapping else 1,
                "Modality": mapping.modality if mapping else default_modality,
            }
        )
    return review_rows


def cart_rows_to_grocery_items(cart_rows: list[dict[str, object]]) -> list[GroceryItem]:
    grocery_items = []
    for row in cart_rows:
        recipes = tuple(
            recipe.strip()
            for recipe in str(row.get("Recipes", "")).split(",")
            if recipe.strip()
        )
        grocery_items.append(
            GroceryItem(
                ingredient_name=str(row["Ingredient"]),
                quantity=float(row["Quantity"]),
                unit=str(row["Unit"]),
                recipe_sources=recipes,
            )
        )
    return grocery_items


def mappings_from_product_review_rows(rows: object) -> dict[tuple[str, str], ProductMapping]:
    mappings: dict[tuple[str, str], ProductMapping] = {}
    for row in iter_table_rows(rows):
        product_name = str(row.get("Product name") or "").strip()
        upc = str(row.get("UPC") or "").strip()
        if not product_name or not upc:
            continue
        ingredient = normalize_ingredient_name(str(row.get("Ingredient", "")))
        unit = normalize_unit(str(row.get("Unit", "each")))
        mappings[(ingredient, unit)] = ProductMapping(
            ingredient_name=ingredient,
            unit=unit,
            product_name=product_name,
            upc=upc,
            cart_quantity=int(row.get("Cart quantity") or 1),
            modality=str(row.get("Modality") or "PICKUP"),
        )
    return mappings


def iter_table_rows(rows: object) -> list[dict[str, object]]:
    if hasattr(rows, "to_dict"):
        return list(rows.to_dict("records"))
    return [dict(row) for row in rows]  # type: ignore[arg-type]


def render_recipes_tab(repository: RecipeRepository) -> None:
    left, right = st.columns([1, 1])

    with left:
        st.subheader("Recipe Library")
        recipes = repository.list_recipe_summaries()
        selected_recipe_name = st.selectbox(
            "Recipe",
            options=[recipe.name for recipe in recipes],
            index=0 if recipes else None,
        )

        if selected_recipe_name:
            selected_summary = next(recipe for recipe in recipes if recipe.name == selected_recipe_name)
            recipe = repository.get_recipe(selected_summary.id)
            st.markdown(f"**Servings:** {format_quantity(recipe.servings)}")
            st.dataframe(
                [
                    {
                        "Ingredient": ingredient.ingredient_name,
                        "Quantity": format_quantity(ingredient.quantity),
                        "Unit": ingredient.unit,
                        "Preparation": ingredient.preparation or "",
                    }
                    for ingredient in recipe.ingredients
                ],
                use_container_width=True,
                hide_index=True,
            )
            if recipe.steps:
                for index, step in enumerate(recipe.steps, start=1):
                    st.markdown(f"{index}. {step}")

    with right:
        st.subheader("Add Recipe")
        render_add_recipe_form(repository)


def render_add_recipe_form(repository: RecipeRepository) -> None:
    known_ingredients = repository.list_known_ingredients()
    if "ingredient_row_count" not in st.session_state:
        st.session_state.ingredient_row_count = 4

    name = st.text_input("Name")
    servings = st.number_input("Servings", min_value=1.0, value=4.0, step=1.0)

    st.markdown("**Ingredients**")
    st.caption("Start typing an ingredient. Close matches from your recipe library will be suggested automatically.")
    ingredient_rows: list[dict[str, object]] = []
    for index in range(st.session_state.ingredient_row_count):
        columns = st.columns([2.2, 0.9, 1, 1.3])
        with columns[0]:
            ingredient_name = st.text_input(
                "Ingredient",
                key=f"ingredient-name-{index}",
                placeholder="yellow onion",
                label_visibility="collapsed",
            )
        with columns[1]:
            quantity = st.number_input(
                "Qty",
                min_value=0.0,
                value=0.0,
                step=0.25,
                key=f"ingredient-quantity-{index}",
                label_visibility="collapsed",
            )
        with columns[2]:
            unit = st.selectbox(
                "Unit",
                options=[
                    "each",
                    "clove",
                    "can",
                    "package",
                    "bag",
                    "tsp",
                    "tbsp",
                    "cup",
                    "oz",
                    "lb",
                    "g",
                    "kg",
                ],
                key=f"ingredient-unit-{index}",
                label_visibility="collapsed",
            )
        with columns[3]:
            preparation = st.text_input(
                "Prep",
                key=f"ingredient-preparation-{index}",
                placeholder="diced",
                label_visibility="collapsed",
            )

        if ingredient_name.strip():
            normalized_name = normalize_ingredient_name(ingredient_name)
            suggestion = get_best_ingredient_match(normalized_name, known_ingredients)
            if suggestion and suggestion != normalized_name:
                st.caption(f"Ingredient {index + 1}: did you mean '{suggestion}'?")
            final_name = suggestion or normalized_name
            ingredient_rows.append(
                {
                    "ingredient_name": final_name,
                    "quantity": quantity,
                    "unit": unit,
                    "preparation": preparation.strip() or None,
                    "raw_text": build_raw_ingredient_text(final_name, quantity, unit, preparation),
                }
            )

    controls = st.columns([1, 1, 3])
    with controls[0]:
        if st.button("Add Row"):
            st.session_state.ingredient_row_count += 1
            st.rerun()
    with controls[1]:
        if st.button("Remove Row", disabled=st.session_state.ingredient_row_count <= 1):
            st.session_state.ingredient_row_count -= 1
            st.rerun()

    warnings = validate_ingredient_rows(ingredient_rows)
    for warning in warnings:
        st.warning(warning)

    step_text = st.text_area(
        "Instructions",
        placeholder="Optional: one step per line",
        height=120,
    )
    source = st.text_input("Source", value="User recipe")

    if st.button("Save Recipe", type="primary"):
        try:
            if not name.strip():
                raise ValueError("Recipe name is required.")
            if not ingredient_rows:
                raise ValueError("Add at least one ingredient before saving a recipe.")
            if warnings:
                raise ValueError("Resolve duplicate or similar ingredient warnings before saving.")
            for ingredient in ingredient_rows:
                if float(ingredient["quantity"]) <= 0:
                    raise ValueError("Every ingredient needs a quantity greater than zero.")

            steps = [line.strip() for line in step_text.splitlines() if line.strip()]
            repository.add_recipe(
                name=name,
                servings=servings,
                ingredients=ingredient_rows,
                steps=steps,
                source=source or None,
            )
        except (KeyError, ValueError) as exc:
            st.error(str(exc))
        else:
            st.success(f"Saved recipe '{name}'.")
            st.rerun()


def render_configuration_tab(repository: RecipeRepository) -> None:
    st.subheader("Configuration")
    st.markdown("**Vendor Connections**")
    st.caption("Future vendor sign-in, API credentials, and order preferences will live here.")
    st.dataframe(
        [
            {"Vendor": vendor, "Status": status, "Connection": "Not connected"}
            for vendor, status in VENDOR_STATUS.items()
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("**Saved Product Preferences**")
    mappings = repository.list_product_mappings()
    if not mappings:
        st.info("No product mappings saved yet.")
        return

    st.dataframe(
        [
            {
                "Ingredient": mapping.ingredient_name,
                "Unit": mapping.unit,
                "Product": mapping.product_name,
                "UPC": mapping.upc,
                "Cart quantity": mapping.cart_quantity,
                "Brand": mapping.brand or "",
                "Package": mapping.package_size or "",
                "Location": mapping.location_id,
                "Modality": mapping.modality,
            }
            for mapping in mappings
        ],
        use_container_width=True,
        hide_index=True,
    )


def get_best_ingredient_match(name: str, known_ingredients: list[str]) -> str | None:
    if not name or not known_ingredients:
        return None
    if name in known_ingredients:
        return name
    matches = get_close_matches(name, known_ingredients, n=1, cutoff=0.9)
    return matches[0] if matches else None


def build_raw_ingredient_text(name: str, quantity: float, unit: str, preparation: str | None) -> str:
    raw = f"{format_quantity(quantity)} {unit} {name}"
    if preparation:
        raw = f"{raw}, {preparation.strip()}"
    return raw


def validate_ingredient_rows(ingredient_rows: list[dict[str, object]]) -> list[str]:
    warnings: list[str] = []
    normalized_names = [normalize_ingredient_name(str(row["ingredient_name"])) for row in ingredient_rows]
    duplicates = sorted({name for name in normalized_names if normalized_names.count(name) > 1})
    for duplicate in duplicates:
        warnings.append(f"Duplicate ingredient: '{duplicate}'. Combine it into one row.")

    for index, name in enumerate(normalized_names):
        other_names = normalized_names[:index] + normalized_names[index + 1 :]
        matches = get_close_matches(name, other_names, n=1, cutoff=0.88)
        if matches and matches[0] != name:
            first, second = sorted((name, matches[0]))
            warning = (
                f"Similar ingredients detected: '{first}' and '{second}'. "
                "Use one shared name if they are the same item."
            )
            if warning not in warnings:
                warnings.append(warning)

    return warnings


def parse_ingredient_lines(text: str) -> list[dict[str, object]]:
    ingredients: list[dict[str, object]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        parts = [part.strip() for part in line.split("|")]
        if len(parts) < 3:
            raise ValueError(
                f"Ingredient line {line_number} must include name, quantity, and unit separated by '|'."
            )
        try:
            quantity = float(parts[1])
        except ValueError as exc:
            raise ValueError(f"Ingredient line {line_number} has an invalid quantity.") from exc

        ingredients.append(
            {
                "ingredient_name": parts[0],
                "quantity": quantity,
                "unit": parts[2],
                "preparation": parts[3] if len(parts) > 3 and parts[3] else None,
                "raw_text": line.strip(),
            }
        )

    if not ingredients:
        raise ValueError("Add at least one ingredient before saving a recipe.")
    return ingredients


if __name__ == "__main__":
    main()
