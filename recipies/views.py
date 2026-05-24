from django.http import HttpResponse
from django.shortcuts import render
from django.views import generic

from recipies.models import Recipe

class IndexView(generic.ListView):

    def get_queryset(self):
        return Recipe.objects.all()

class DetailView(generic.DetailView):
    model = Recipe