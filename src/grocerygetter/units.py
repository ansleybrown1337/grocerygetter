"""Small unit helpers for deterministic grocery-list aggregation."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


UNIT_ALIASES = {
    "": "each",
    "each": "each",
    "item": "each",
    "items": "each",
    "whole": "each",
    "clove": "clove",
    "cloves": "clove",
    "can": "can",
    "cans": "can",
    "package": "package",
    "packages": "package",
    "pkg": "package",
    "bag": "bag",
    "bags": "bag",
    "tsp": "tsp",
    "teaspoon": "tsp",
    "teaspoons": "tsp",
    "tbsp": "tbsp",
    "tablespoon": "tbsp",
    "tablespoons": "tbsp",
    "cup": "cup",
    "cups": "cup",
    "pint": "pint",
    "pints": "pint",
    "quart": "quart",
    "quarts": "quart",
    "gallon": "gallon",
    "gallons": "gallon",
    "oz": "oz",
    "ounce": "oz",
    "ounces": "oz",
    "lb": "lb",
    "lbs": "lb",
    "pound": "lb",
    "pounds": "lb",
    "g": "g",
    "gram": "g",
    "grams": "g",
    "kg": "kg",
    "kilogram": "kg",
    "kilograms": "kg",
}

VOLUME_TO_CUP = {
    "tsp": 1 / 48,
    "tbsp": 1 / 16,
    "cup": 1,
    "pint": 2,
    "quart": 4,
    "gallon": 16,
}

US_MASS_TO_OZ = {
    "oz": 1,
    "lb": 16,
}

METRIC_MASS_TO_G = {
    "g": 1,
    "kg": 1000,
}


def normalize_unit(unit: str | None) -> str:
    """Return the canonical form of a common cooking unit."""

    value = (unit or "").strip().lower()
    return UNIT_ALIASES.get(value, value or "each")


def normalize_ingredient_name(name: str) -> str:
    """Normalize ingredient names for grouping while preserving readability."""

    return " ".join(name.strip().lower().split())


def quantity_for_aggregation(quantity: float, unit: str) -> tuple[float, str]:
    """Convert compatible units into a shared unit for summing."""

    normalized_unit = normalize_unit(unit)

    if normalized_unit in VOLUME_TO_CUP:
        return quantity * VOLUME_TO_CUP[normalized_unit], "cup"

    if normalized_unit in US_MASS_TO_OZ:
        return quantity * US_MASS_TO_OZ[normalized_unit], "oz"

    if normalized_unit in METRIC_MASS_TO_G:
        return quantity * METRIC_MASS_TO_G[normalized_unit], "g"

    return quantity, normalized_unit


def format_quantity(quantity: float) -> str:
    """Format quantities without noisy binary floating point artifacts."""

    decimal_value = Decimal(str(quantity)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
    decimal_value = decimal_value.normalize()
    text = format(decimal_value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text
