from django.test import TestCase
from django.urls import reverse


class RecipeSearchTests(TestCase):
    def test_search_matches_recipe_ingredients(self):
        response = self.client.get(reverse('recipe_list'), {'q': 'cumin'})

        self.assertEqual(response.status_code, 200)
        recipes = list(response.context['recipes'])
        titles = {recipe.title for recipe in recipes}

        self.assertIn('Kabsa', titles)
        self.assertIn('Jareesh', titles)
        self.assertNotIn('Chicken Fried Rice', titles)
