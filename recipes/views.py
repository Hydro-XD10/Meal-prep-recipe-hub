import os
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from django.core.files import File
from django.db.models import Q
from .models import Recipe, Favourite
from .forms import SignUpForm, RecipeForm


def _seed_initial_recipes():

    keep_titles = ['Kabsa', 'Chicken Fried Rice', 'Lamb with Scallions', 'Moo-Shu Pork', 'Pork with Preserved Greens', 'Jareesh']
    Recipe.objects.exclude(title__in=keep_titles).delete()

    creator_specs = {
        'XiaobeiTang': 'xiaobeitang@example.com',
        'XinhaoZhang': 'xinhaozhang@example.com',
        'Abdulmalik Alamri': 'abdulmalik.alamri@example.com',
    }
    creators = {}
    for username, email in creator_specs.items():
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email}
        )
        if created:
            user.set_password('recipe1234')
            user.save()
        creators[username] = user

    initial_data = [
        {
            'title': 'Chicken Fried Rice',
            'ingredients': 'Cooked rice\nChicken pieces\nEggs\nCarrots\nPeas\nSoy sauce\nGreen onion',
            'steps': '1. Heat oil and stir-fry chicken until cooked.\n2. Add vegetables and cooked rice.\n3. Push rice to side, scramble eggs, then mix.\n4. Add soy sauce and stir evenly.',
            'cooking_time': 20,
            'difficulty': 'Easy',
            'creator_username': 'XiaobeiTang',
        },
        {
            'title': 'Lamb with Scallions',
            'ingredients': 'Lamb slices 500g\nEgg white 1\nScallion 0.5 stalk\nGinger 3 slices\nSalt 0.5 tbsp\nCornstarch 1 tbsp + 0.5 tbsp\nWater 4 tbsp\nSoy sauce 1 tbsp\nCooking wine 2 tbsp\nChicken bouillon powder 0.33 tbsp\nSesame oil 0.5 tbsp\nCooking oil 5 tbsp',
            'steps': '1. Marinate lamb with salt, egg white, cornstarch and water for 10 minutes.\n2. Cut scallion diagonally.\n3. Prepare sauce with salt, soy sauce, cooking wine, chicken powder, cornstarch, and water.\n4. Heat oil, cook scallion and ginger, then add lamb for 1 minute.\n5. Add cooking wine and sesame oil, then add sauce and stir-fry before serving.',
            'cooking_time': 25,
            'difficulty': 'Medium',
            'creator_username': 'XinhaoZhang',
            'image_path': 'media/recipe_images/Lamb with Scallions.png',
            'image_name': 'Lamb with Scallions.png',
        },
        {
            'title': 'Kabsa',
            'ingredients': '1 whole chicken or 4 chicken pieces\n2 cups basmati rice\n1 large onion chopped\n2 tomatoes chopped or blended\n2 tbsp tomato paste\n3 cloves garlic minced\n2 carrots grated\n3 tbsp oil\n4 cups water\n1 black lime dried\n1 bay leaf\n1 cinnamon stick\n4 cloves\n4 cardamom pods\n1 tsp cumin\n1 tsp coriander\n1 tsp paprika\n1/2 tsp turmeric\nSalt and black pepper to taste\nRaisins and almonds (optional)',
            'steps': '1. Wash and soak rice 20 minutes, then drain.\n2. Heat oil in a large pot, cook onion until soft and golden.\n3. Add garlic for a few seconds.\n4. Add tomatoes and tomato paste, cook until thick.\n5. Add spices, salt, and pepper.\n6. Mix chicken into spices, add water, black lime, bay leaf, cinnamon, cloves, cardamom and cook until chicken done.\n7. Remove chicken, add carrot and rice to broth, cook low heat until rice done.\n8. Optional: grill chicken for colour, then plate rice and chicken, add raisins and almonds.',
            'cooking_time': 45,
            'difficulty': 'Medium',
            'creator_username': 'Abdulmalik Alamri',
            'image_path': 'media/recipe_images/Kabsa.png',
            'image_name': 'Kabsa.png',
        },
        {
            'title': 'Moo-Shu Pork',
            'ingredients': 'Pork tenderloin 300g\nDried black fungus 3 pieces\nCucumber 1\nEggs 2\nDried daylily 10g\nSalt 3g\nSoy sauce 15ml\nCooking wine 3ml\nSesame oil 1ml\nCornstarch slurry as needed\nSugar 3g\nGarlic 8 cloves\nVegetable oil as needed',
            'steps': '1. Soak the black fungus and dried daylily in cold water for 1 hour, then wash them. Tear the black fungus into small pieces, cut the daylily into sections, slice the garlic, and cut the cucumber into diamond-shaped slices.\n2. Slice the pork tenderloin thinly, mix with cooking wine and cornstarch, and marinate for 5 minutes. Beat the eggs with a little water and a few drops of cooking wine.\n3. Heat oil in a wok, pour in the egg mixture, scramble quickly, and set aside.\n4. Add a little more oil, stir-fry the garlic until fragrant, then add the pork and cook until it changes color. Add the black fungus, daylily, soy sauce, salt, sugar, and a little water, then stir-fry for 2 minutes.\n5. Return the eggs and add the cucumber. Stir well, pour in a little cornstarch slurry to thicken, and serve.',
            'cooking_time': 15,
            'difficulty': 'Medium',
            'creator_username': 'XinhaoZhang',
            'image_path': 'media/recipe_images/Moo-Shu-Pork.png',
            'image_name': 'Moo-Shu-Pork.png',
        },
        {
            'title': 'Pork with Preserved Greens',
            'ingredients': 'Preserved greens 200g\nShredded pork 150g\nDried chilies 2 to 3\nGinger, a little\nCornstarch 1 tsp\nLight soy sauce 1 tbsp\nSugar 1/2 tsp\nSalt, a little\nCooking wine 1 tbsp\nVegetable oil as needed',
            'steps': '1. Soak the preserved greens in lightly salted water for about 30 minutes to reduce some of the saltiness. Rinse well, squeeze out the excess water, and chop into small pieces.\n2. Cut the pork into thin strips. Add cooking wine, a little salt, cornstarch, and a small amount of sugar, then mix well and marinate for 10 minutes.\n3. Heat a little extra oil in a wok and quickly stir-fry the pork until it changes color. Remove and set aside.\n4. Using the oil left in the wok, stir-fry the dried chilies and ginger until fragrant, then add the preserved greens and stir well.\n5. Return the pork to the wok, add a little light soy sauce and a bit more sugar, then stir-fry for 1 to 2 minutes until everything is well combined. Serve hot.',
            'cooking_time': 15,
            'difficulty': 'Easy',
            'creator_username': 'XiaobeiTang',
            'image_path': 'media/recipe_images/Pork with Preserved Greens.png',
            'image_name': 'Pork with Preserved Greens.png',
        },
        {
            'title': 'Jareesh',
            'ingredients': 'Jareesh (crushed wheat) 1 cup\nLaban or plain yogurt 2 cups\nOnion 1, finely chopped\nButter or oil 2 tbsp\nWater 2 cups\nMilk 1 cup\nSalt\nBlack pepper\nCumin 1/2 tsp',
            'steps': '1. Wash the jareesh well and soak it for about 30 minutes.\n2. Heat butter or oil in a pot and cook the onion until soft.\n3. Add the soaked jareesh and stir for 2 minutes.\n4. Add water, salt, black pepper, and cumin, then cover and cook on low heat, stirring from time to time.\n5. When the jareesh becomes soft, add the milk and laban.\n6. Keep stirring until it becomes creamy and thick, then cook for a few more minutes on low heat.\n7. Serve hot.',
            'cooking_time': 45,
            'difficulty': 'Medium',
            'creator_username': 'Abdulmalik Alamri',
            'image_path': 'media/recipe_images/Jareesh.png',
            'image_name': 'Jareesh.png',
        },
    ]

    for recipe_data in initial_data:
        creator = creators[recipe_data['creator_username']]
        recipe = Recipe.objects.update_or_create(
            title=recipe_data['title'],
            defaults={
                **{
                    k: v for k, v in recipe_data.items()
                    if k not in ['image_path', 'image_name', 'creator_username']
                },
                'creator': creator
            }
        )[0]
        if recipe_data.get('image_path'):
            try:
                desired_image_name = f"recipe_images/{recipe_data['image_name']}"
                current_image_name = recipe.image.name or ''

                if current_image_name != desired_image_name:
                    if os.path.exists(recipe_data['image_path']):
                        recipe.image.name = desired_image_name
                        recipe.save(update_fields=['image'])
                    else:
                        with open(recipe_data['image_path'], 'rb') as f:
                            recipe.image.save(recipe_data['image_name'], File(f), save=False)
                        recipe.save(update_fields=['image'])
            except FileNotFoundError:
                pass  


def recipe_list(request):
    _seed_initial_recipes()
    query = request.GET.get('q')

    if query:
        recipes = Recipe.objects.filter(
            Q(title__icontains=query) | Q(ingredients__icontains=query)
        ).distinct()
    else:
        recipes = Recipe.objects.all()

    favourite_recipes = []
    if request.user.is_authenticated:
        favourite_recipes = Recipe.objects.filter(favourite__user=request.user)

    return render(request, 'recipes/recipe_list.html', {
        'recipes': recipes,
        'query': query,
        'favourite_recipes': favourite_recipes,
    })


def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    recipe.view_count += 1
    recipe.save()

    is_favourite = False
    if request.user.is_authenticated:
        is_favourite = Favourite.objects.filter(user=request.user, recipe=recipe).exists()

    return render(request, 'recipes/recipe_detail.html', {
        'recipe': recipe,
        'is_favourite': is_favourite,
        'is_favourited': is_favourite,
    })


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('recipe_list')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})


@login_required
def create_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.creator = request.user
            recipe.save()
            return redirect('recipe_detail', recipe_id=recipe.id)
    else:
        form = RecipeForm()

    return render(request, 'recipes/recipe_form.html', {
        'form': form,
        'page_title': 'Create Recipe'
    })


@login_required
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if recipe.creator != request.user:
        return HttpResponseForbidden("you are not allowed to edit this recipe")

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect('recipe_detail', recipe_id=recipe.id)
    else:
        form = RecipeForm(instance=recipe)

    return render(request, 'recipes/recipe_form.html', {
        'form': form,
        'page_title': 'Edit Recipe'
    })


@login_required
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if recipe.creator != request.user:
        return HttpResponseForbidden("you are not allowed to delete this recipe")

    if request.method == 'POST':
        recipe.delete()
        return redirect('recipe_list')

    return render(request, 'recipes/delete_recipe.html', {'recipe': recipe})


@login_required
def add_favourite(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    Favourite.objects.get_or_create(user=request.user, recipe=recipe)
    return redirect('recipe_detail', recipe_id=recipe.id)


@login_required
def remove_favourite(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    Favourite.objects.filter(user=request.user, recipe=recipe).delete()
    return redirect('recipe_detail', recipe_id=recipe.id)


@login_required
def my_favourites(request):
    favourites = Favourite.objects.filter(user=request.user).select_related('recipe').order_by('-created_at')
    return render(request, 'recipes/my_favourites.html', {'favourites': favourites})
@login_required
def my_recipes(request):
    recipes = Recipe.objects.filter(creator=request.user).order_by('-created_at')
    return render(request, 'recipes/my_recipes.html', {
        'recipes': recipes,
    })


@login_required
def weekly_plan(request):
    # Placeholder implementation - can be extended with a real planning model
    return render(request, 'recipes/weekly_plan.html')
