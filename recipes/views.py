from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Recipe, Favourite
from .forms import SignUpForm, RecipeForm


def recipe_list(request):
    query = request.GET.get('q')

    if query:
        recipes = Recipe.objects.filter(title__icontains=query)
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
