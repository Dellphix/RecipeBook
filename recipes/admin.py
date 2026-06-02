from django.contrib import admin
from django.db import models

from .models import Recipe, Tag

class RecipeAdmin(admin.ModelAdmin):
    exclude = ['uuid']


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)