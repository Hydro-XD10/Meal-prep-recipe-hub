from django.db import models
from django.contrib.auth.models import User

class Recipe(models.Model):

    title = models.CharField(max_length=200)

    image = models.ImageField(upload_to='recipe_images/', null=True, blank=True)

    ingredients = models.TextField()

    steps = models.TextField()

    cooking_time = models.PositiveIntegerField()

    DIFFICULTY_CHOICES = [
        ("Easy", "Easy"),
        ("Medium", "Medium"),
        ("Hard", "Hard"),
    ]

    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES
    )

    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    view_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def favourite_count(self):
        return Favourite.objects.filter(recipe=self).count()

    def like_count(self):
        return Like.objects.filter(recipe=self).count()

    def __str__(self):
        return self.title
    
class Favourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f"{self.user.username} favourited {self.recipe.title}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f"{self.user.username} liked {self.recipe.title}"