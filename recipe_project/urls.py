from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from recipes import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('accounts/', include('django.contrib.auth.urls')),

    path('', views.recipe_list, name='recipe_list'),
    path('signup/', views.signup_view, name='signup'),

    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('recipe/create/', views.create_recipe, name='create_recipe'),
    path('recipe/<int:recipe_id>/edit/', views.edit_recipe, name='edit_recipe'),
    path('recipe/<int:recipe_id>/delete/', views.delete_recipe, name='delete_recipe'),

    path('recipe/<int:recipe_id>/favourite/', views.add_favourite, name='add_favourite'),
    path('recipe/<int:recipe_id>/unfavourite/', views.remove_favourite, name='remove_favourite'),

    path('recipe/<int:recipe_id>/like/', views.add_like, name='add_like'),
    path('recipe/<int:recipe_id>/unlike/', views.remove_like, name='remove_like'),

    path('my-favourites/', views.my_favourites, name='my_favourites'),
    path('my-recipes/', views.my_recipes, name='my_recipes'),
    path('plan/', views.weekly_plan, name='weekly_plan'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)