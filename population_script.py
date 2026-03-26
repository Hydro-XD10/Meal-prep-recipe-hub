#!/usr/bin/env python
"""Populate the database with the sample recipes used by the project."""

from __future__ import annotations

import os
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parent
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "recipe_project.settings")

    import django

    django.setup()

    from recipes.models import Recipe
    from recipes.views import _seed_initial_recipes

    before_count = Recipe.objects.count()
    _seed_initial_recipes()
    after_count = Recipe.objects.count()

    print("Population script completed successfully.")
    print(f"Recipes before: {before_count}")
    print(f"Recipes after: {after_count}")


if __name__ == "__main__":
    main()
