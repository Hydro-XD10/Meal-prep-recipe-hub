from django.contrib import admin
from .models import Recipe, Favourite, Like

admin.site.register(Recipe)
admin.site.register(Favourite)
admin.site.register(Like)
