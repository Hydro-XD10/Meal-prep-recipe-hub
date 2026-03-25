from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Recipe, Favourite, Like, WeeklyPlanEntry


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


class AuthAndRecipeFeatureTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            password="recipe1234"
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            password="recipe1234"
        )

        self.recipe = Recipe.objects.create(
            title="Owner Recipe",
            ingredients="Rice and chicken",
            steps="Cook everything",
            cooking_time=30,
            difficulty="Easy",
            creator=self.owner,
        )

    def test_signup_page_loads(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)

    def test_user_can_signup(self):
        response = self.client.post(reverse("signup"), {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "StrongPassword123",
            "password2": "StrongPassword123",
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_create_recipe_requires_login(self):
        response = self.client.get(reverse("create_recipe"))
        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_can_create_recipe(self):
        self.client.login(username="owner", password="recipe1234")

        response = self.client.post(reverse("create_recipe"), {
            "title": "New Soup",
            "ingredients": "Water and vegetables",
            "steps": "Boil and serve",
            "cooking_time": 15,
            "difficulty": "Easy",
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Recipe.objects.filter(title="New Soup").exists())

        created_recipe = Recipe.objects.get(title="New Soup")
        self.assertEqual(created_recipe.creator, self.owner)

    def test_owner_can_edit_own_recipe(self):
        self.client.login(username="owner", password="recipe1234")

        response = self.client.post(reverse("edit_recipe", args=[self.recipe.id]), {
            "title": "Updated Owner Recipe",
            "ingredients": "Rice and chicken",
            "steps": "Cook slowly",
            "cooking_time": 35,
            "difficulty": "Medium",
        })

        self.assertEqual(response.status_code, 302)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.title, "Updated Owner Recipe")
        self.assertEqual(self.recipe.cooking_time, 35)
        self.assertEqual(self.recipe.difficulty, "Medium")

    def test_non_owner_cannot_edit_recipe(self):
        self.client.login(username="otheruser", password="recipe1234")

        response = self.client.post(reverse("edit_recipe", args=[self.recipe.id]), {
            "title": "Hacked Recipe",
            "ingredients": "Bad data",
            "steps": "Bad steps",
            "cooking_time": 1,
            "difficulty": "Easy",
        })

        self.assertEqual(response.status_code, 403)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.title, "Owner Recipe")

    def test_owner_can_delete_own_recipe(self):
        self.client.login(username="owner", password="recipe1234")

        response = self.client.post(reverse("delete_recipe", args=[self.recipe.id]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Recipe.objects.filter(id=self.recipe.id).exists())

    def test_non_owner_cannot_delete_recipe(self):
        self.client.login(username="otheruser", password="recipe1234")

        response = self.client.post(reverse("delete_recipe", args=[self.recipe.id]))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Recipe.objects.filter(id=self.recipe.id).exists())

    def test_add_favourite_requires_login(self):
        response = self.client.get(reverse("add_favourite", args=[self.recipe.id]))
        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_can_add_favourite(self):
        self.client.login(username="otheruser", password="recipe1234")

        response = self.client.get(reverse("add_favourite", args=[self.recipe.id]))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Favourite.objects.filter(user=self.other_user, recipe=self.recipe).exists()
        )

    def test_logged_in_user_can_remove_favourite(self):
        Favourite.objects.create(user=self.other_user, recipe=self.recipe)
        self.client.login(username="otheruser", password="recipe1234")

        response = self.client.get(reverse("remove_favourite", args=[self.recipe.id]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Favourite.objects.filter(user=self.other_user, recipe=self.recipe).exists()
        )

    def test_add_like_requires_login(self):
        response = self.client.get(reverse("add_like", args=[self.recipe.id]))
        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_can_add_like(self):
        self.client.login(username="otheruser", password="recipe1234")

        response = self.client.get(reverse("add_like", args=[self.recipe.id]))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Like.objects.filter(user=self.other_user, recipe=self.recipe).exists()
        )

    def test_logged_in_user_can_remove_like(self):
        Like.objects.create(user=self.other_user, recipe=self.recipe)
        self.client.login(username="otheruser", password="recipe1234")

        response = self.client.get(reverse("remove_like", args=[self.recipe.id]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Like.objects.filter(user=self.other_user, recipe=self.recipe).exists()
        )

    def test_my_favourites_requires_login(self):
        response = self.client.get(reverse("my_favourites"))
        self.assertEqual(response.status_code, 302)

    def test_my_recipes_requires_login(self):
        response = self.client.get(reverse("my_recipes"))
        self.assertEqual(response.status_code, 302)

    def test_my_recipes_shows_only_logged_in_users_recipes(self):
        Recipe.objects.create(
            title="Other User Recipe",
            ingredients="Pasta",
            steps="Boil",
            cooking_time=10,
            difficulty="Easy",
            creator=self.other_user,
        )

        self.client.login(username="owner", password="recipe1234")
        response = self.client.get(reverse("my_recipes"))

        self.assertEqual(response.status_code, 200)
        recipes = list(response.context["recipes"])
        titles = {recipe.title for recipe in recipes}

        self.assertIn("Owner Recipe", titles)
        self.assertNotIn("Other User Recipe", titles)