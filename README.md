# Meal Prep Recipe Hub

A Django web application for browsing, saving, and planning meals with recipe data.

Tested with Python 3.13.

## Project Links

- GitHub repository: https://github.com/Hydro-XD10/Meal-prep-recipe-hub
- PythonAnywhere deployment: https://xbt.pythonanywhere.com

## Main Features

- Browse a list of recipes
- View recipe details, including ingredients, steps, cooking time, difficulty, and creator
- Search recipes by keyword
- Register, log in, and log out
- Create, edit, and delete your own recipes
- Favourite and like recipes
- Build a simple weekly meal plan

## Requirements

Install the project dependencies with:

```bash
pip install -r requirements.txt
```

## Local Setup

Run the following commands from the main project folder:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python population_script.py
python manage.py runserver
```

## Population Script

This project includes a root-level population script:

```bash
python population_script.py
```

It inserts the sample users and recipe data used by the application. The script is safe to run multiple times and does not duplicate the seeded recipes.

## Database Note

The SQLite database file is not included in the repository. Create the database locally by running migrations and then execute `population_script.py` to load the sample data.
