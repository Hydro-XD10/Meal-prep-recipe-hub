from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Recipe, WeeklyPlanEntry


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'image', 'ingredients', 'steps', 'cooking_time', 'difficulty']


class WeeklyPlanForm(forms.Form):
    monday = forms.ModelChoiceField(queryset=Recipe.objects.none(), required=False)
    tuesday = forms.ModelChoiceField(queryset=Recipe.objects.none(), required=False)
    wednesday = forms.ModelChoiceField(queryset=Recipe.objects.none(), required=False)
    thursday = forms.ModelChoiceField(queryset=Recipe.objects.none(), required=False)
    friday = forms.ModelChoiceField(queryset=Recipe.objects.none(), required=False)
    saturday = forms.ModelChoiceField(queryset=Recipe.objects.none(), required=False)
    sunday = forms.ModelChoiceField(queryset=Recipe.objects.none(), required=False)

    def __init__(self, *args, **kwargs):
        recipes = kwargs.pop("recipes", Recipe.objects.all())
        super().__init__(*args, **kwargs)

        recipe_queryset = recipes.order_by("title")
        for day_key, _day_label in WeeklyPlanEntry.DAY_CHOICES:
            self.fields[day_key].queryset = recipe_queryset
            self.fields[day_key].empty_label = "No recipe selected"
            self.fields[day_key].label = _day_label
            self.fields[day_key].widget.attrs.update({"class": "form-select"})
