"""Helpers for selecting recipes without recency or favorites bias."""

from __future__ import annotations

import random
from collections.abc import Sequence


def choose_random_recipe_names(
    recipe_names: Sequence[str],
    count: int,
    *,
    rng: random.Random | None = None,
) -> list[str]:
    """Return up to ``count`` random recipe names without duplicates."""

    if count <= 0 or not recipe_names:
        return []

    chooser = rng or random
    return chooser.sample(list(recipe_names), k=min(count, len(recipe_names)))
