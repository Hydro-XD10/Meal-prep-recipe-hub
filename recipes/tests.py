from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Recipe, WeeklyPlanEntry


class RecipeSearchTests(TestCase):
    def test_search_matches_recipe_ingredients(self):
        response = self.client.get(reverse('recipe_list'), {'q': 'cumin'})

        self.assertEqual(response.status_code, 200)
        recipes = list(response.context['recipes'])
        titles = {recipe.title for recipe in recipes}

        self.assertIn('Kabsa', titles)
        self.assertIn('Jareesh', titles)
        self.assertNotIn('Chicken Fried Rice', titles)

    def test_recipe_list_does_not_delete_user_created_recipe(self):
        user = User.objects.create_user(username="cook", password="recipe1234")
        custom_recipe = Recipe.objects.create(
            title="My Custom Noodles",
            ingredients="Noodles",
            steps="Cook and serve",
            cooking_time=12,
            difficulty="Easy",
            creator=user,
        )

        response = self.client.get(reverse("recipe_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Recipe.objects.filter(id=custom_recipe.id).exists())

    def test_recipe_list_does_not_overwrite_user_recipe_with_seed_title(self):
        user = User.objects.create_user(username="duplicate-title-user", password="recipe1234")
        custom_recipe = Recipe.objects.create(
            title="Kabsa",
            ingredients="User ingredients",
            steps="User steps",
            cooking_time=5,
            difficulty="Easy",
            creator=user,
        )

        response = self.client.get(reverse("recipe_list"))

        self.assertEqual(response.status_code, 200)
        custom_recipe.refresh_from_db()
        self.assertEqual(custom_recipe.ingredients, "User ingredients")
        self.assertEqual(custom_recipe.steps, "User steps")
        self.assertEqual(custom_recipe.cooking_time, 5)


class WeeklyPlanTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="planner", password="recipe1234")
        self.recipe_one = Recipe.objects.create(
            title="Plan A",
            ingredients="Rice",
            steps="Cook",
            cooking_time=10,
            difficulty="Easy",
            creator=self.user,
        )
        self.recipe_two = Recipe.objects.create(
            title="Plan B",
            ingredients="Pasta",
            steps="Boil",
            cooking_time=20,
            difficulty="Medium",
            creator=self.user,
        )

    def test_weekly_plan_requires_login(self):
        response = self.client.get(reverse("weekly_plan"))
        self.assertEqual(response.status_code, 302)

    def test_weekly_plan_loads_existing_entries(self):
        WeeklyPlanEntry.objects.create(
            user=self.user,
            day_of_week="monday",
            recipe=self.recipe_one,
        )
        self.client.login(username="planner", password="recipe1234")

        response = self.client.get(reverse("weekly_plan"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["form"].initial["monday"], self.recipe_one)

    def test_weekly_plan_saves_and_clears_entries(self):
        WeeklyPlanEntry.objects.create(
            user=self.user,
            day_of_week="tuesday",
            recipe=self.recipe_one,
        )
        self.client.login(username="planner", password="recipe1234")

        response = self.client.post(reverse("weekly_plan"), {
            "monday": self.recipe_two.id,
            "tuesday": "",
            "wednesday": "",
            "thursday": "",
            "friday": "",
            "saturday": "",
            "sunday": "",
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            WeeklyPlanEntry.objects.filter(
                user=self.user,
                day_of_week="monday",
                recipe=self.recipe_two,
            ).exists()
        )
        self.assertFalse(
            WeeklyPlanEntry.objects.filter(
                user=self.user,
                day_of_week="tuesday",
            ).exists()
        )
