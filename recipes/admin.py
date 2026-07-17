from django.contrib import admin
from django.db import models

from .models import Recipe, Tag, Ingredient

class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 1  # Number of extra forms to display

class RecipeAdmin(admin.ModelAdmin):
    exclude = ['uuid']
    inlines = [IngredientInline]


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(Ingredient)