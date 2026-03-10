from django.shortcuts import render, get_object_or_404
from .models import Recipe

def recipe_list(request):
    query = request.GET.get('q')

    if query:
        recipes = Recipe.objects.filter(title__icontains=query)
    else:
        recipes = Recipe.objects.all()

    return render(request, 'recipes/recipe_list.html', {
        'recipes': recipes,
        'query': query
    })

def recipe_detail(request, recipe_id):

    recipe = get_object_or_404(Recipe, id=recipe_id)

    recipe.view_count += 1
    recipe.save()

    return render(request, 'recipes/recipe_detail.html', {'recipe': recipe})